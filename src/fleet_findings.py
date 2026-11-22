import csv
import sys
from collections import Counter, defaultdict

from solutions import merge_sessions, top_faults

DATA = "data/northfield_fleet_events.csv"
DAY = "2026-11-02"
STATES = {"IDLE", "RUNNING", "OVERLOAD", "OVERHEATED", "LOW_BATTERY"}


def load_events(path: str = DATA) -> list[dict[str, str]]:
    with open(path, newline="") as f:
        return [{key: value.strip() for key, value in row.items()} for row in csv.DictReader(f)]


def clean_events(rows: list[dict[str, str]]) -> tuple[list[dict[str, str]], list[tuple[str, dict[str, str]]]]:
    kept: list[dict[str, str]] = []
    removed: list[tuple[str, dict[str, str]]] = []
    first_seen: dict[str, dict[str, str]] = {}
    for row in rows:
        event_id = row["event_id"]
        if event_id in first_seen:
            reason = "duplicate" if row == first_seen[event_id] else "conflicting duplicate"
            removed.append((reason, row))
        elif not row["timestamp"]:
            removed.append(("missing timestamp", row))
        elif not row["timestamp"].startswith(DAY):
            removed.append(("outside reporting day", row))
        elif row["state"] and row["state"] not in STATES:
            removed.append(("unknown state", row))
        elif row["session_start_min"] and int(row["session_start_min"]) > int(row["session_end_min"]):
            removed.append(("session ends before it starts", row))
        else:
            kept.append(row)
        first_seen.setdefault(event_id, row)
    return kept, removed


def fault_summary(kept: list[dict[str, str]], k: int = 3) -> dict:
    codes = [int(row["fault_code"]) for row in kept if row["fault_code"]]
    counts = Counter(codes)
    cutoff = min(counts[code] for code in top_faults(codes, k)) if codes else 0
    rows = [
        {
            "code": code,
            "count": count,
            "share": count / len(codes),
            "in_top_k": count >= cutoff,
        }
        for code, count in counts.most_common()
    ]
    return {"total": len(codes), "cutoff": cutoff, "codes": rows}


def usage_summary(kept: list[dict[str, str]]) -> dict:
    sessions: dict[str, list[list[int]]] = defaultdict(list)
    for row in kept:
        if row["session_start_min"]:
            sessions[row["tool_id"]].append([int(row["session_start_min"]), int(row["session_end_min"])])

    by_tool = []
    for tool in sorted(sessions):
        raw = sum(end - start for start, end in sessions[tool])
        merged = sum(end - start for start, end in merge_sessions(sessions[tool]))
        by_tool.append(
            {
                "tool_id": tool,
                "sessions": len(sessions[tool]),
                "raw_minutes": raw,
                "merged_minutes": merged,
                "double_counted": raw - merged,
            }
        )

    totals = {
        "sessions": sum(item["sessions"] for item in by_tool),
        "raw_minutes": sum(item["raw_minutes"] for item in by_tool),
        "merged_minutes": sum(item["merged_minutes"] for item in by_tool),
        "double_counted": sum(item["double_counted"] for item in by_tool),
    }
    return {"by_tool": by_tool, "totals": totals}


def main(path: str = DATA) -> None:
    rows = load_events(path)
    kept, removed = clean_events(rows)
    reasons = Counter(reason for reason, _ in removed)

    print(f"Loaded {len(rows)} rows, kept {len(kept)}, removed {len(removed)}")
    for reason, count in reasons.most_common():
        print(f"  - {reason}: {count}")

    usage = usage_summary(kept)
    print("\nUsage minutes:")
    for item in usage["by_tool"]:
        print(
            f"  {item['tool_id']}: {item['sessions']:2d} sessions, "
            f"raw={item['raw_minutes']:3d}, merged={item['merged_minutes']:3d}, "
            f"overlap={item['double_counted']:3d}"
        )
    t = usage["totals"]
    print(
        f"  TOTAL:  {t['sessions']:2d} sessions, "
        f"raw={t['raw_minutes']}, merged={t['merged_minutes']}, "
        f"overlap={t['double_counted']} ({t['double_counted'] / t['merged_minutes']:.0%} overstatement)"
    )

    faults = fault_summary(kept)
    print(f"\nFault codes ({faults['total']} total):")
    for item in faults["codes"]:
        tag = " [top 3]" if item["in_top_k"] else ""
        print(f"  {item['code']}: {item['count']} ({item['share']:.0%}){tag}")


if __name__ == "__main__":
    main(*sys.argv[1:])
