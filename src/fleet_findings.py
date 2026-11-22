import csv
import sys
from collections import Counter, defaultdict

from solutions import (
    count_windows,
    group_families,
    labels_match,
    latest_state,
    merge_sessions,
    top_faults,
)

DATA = "data/northfield_fleet_events.csv"
DAY = "2026-11-02"
STATES = {"IDLE", "RUNNING", "OVERLOAD", "OVERHEATED", "LOW_BATTERY"}
SAFETY_STATES = {"OVERLOAD", "OVERHEATED"}
CATALOGUE = ["anchor", "brace", "chisel", "driver", "hammer", "rebar", "socket", "torque"]


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


def _minute_of_day(ts: str) -> int:
    hours, minutes = ts[11:16].split(":")
    return int(hours) * 60 + int(minutes)


def state_summary(kept: list[dict[str, str]]) -> list[dict]:
    events = [(row["tool_id"], row["timestamp"], row["state"]) for row in kept if row["state"]]
    latest = latest_state(events)
    state_time = {tool: max(ts for t, ts, _ in events if t == tool) for tool in latest}

    results = []
    for tool in sorted(latest):
        tool_rows = [row for row in kept if row["tool_id"] == tool]
        minute = _minute_of_day(state_time[tool])
        events_after = [
            row
            for row in tool_rows
            if row["timestamp"] > state_time[tool]
            and ((row["net_energy"] and int(row["net_energy"]) != 0) or row["fault_code"])
        ]
        sessions_after = [
            row for row in tool_rows if row["session_end_min"] and int(row["session_end_min"]) > minute
        ]
        results.append(
            {
                "tool_id": tool,
                "state": latest[tool],
                "time": state_time[tool][11:16],
                "is_safety": latest[tool] in SAFETY_STATES,
                "events_after": len(events_after),
                "sessions_after": len(sessions_after),
                "state_mismatch": (latest[tool] == "IDLE" or latest[tool] in SAFETY_STATES)
                and bool(events_after or sessions_after),
            }
        )
    return results


def part_summary(kept: list[dict[str, str]]) -> dict:
    labels = [row["part_label"] for row in kept if row["part_label"]]
    families = []
    for family in sorted(group_families(labels), key=len, reverse=True):
        part = next((name for name in CATALOGUE if labels_match(name, family[0])), "unknown")
        spellings = sorted(set(family))
        families.append(
            {
                "part": part,
                "scans": len(family),
                "distinct_spellings": len(spellings),
                "spellings": spellings,
            }
        )
    return {
        "total_scans": len(labels),
        "distinct_labels": len(set(labels)),
        "families": families,
    }


def energy_summary(kept: list[dict[str, str]]) -> list[dict]:
    slots: dict[str, list[int]] = defaultdict(list)
    for row in sorted(kept, key=lambda r: r["timestamp"]):
        if row["net_energy"]:
            slots[row["tool_id"]].append(int(row["net_energy"]))
    return [
        {
            "tool_id": tool,
            "slots": len(slots[tool]),
            "net_energy": sum(slots[tool]),
            "zero_windows": count_windows(slots[tool], 0),
        }
        for tool in sorted(slots)
    ]


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

    print("\nLatest tool states:")
    states = state_summary(kept)
    for item in states:
        flag = " [SAFETY]" if item["is_safety"] else ""
        flag += " [MISMATCH]" if item["state_mismatch"] else ""
        print(
            f"  {item['tool_id']}: {item['state']:<11s} at {item['time']}{flag} "
            f"(after: {item['events_after']} events, {item['sessions_after']} sessions)"
        )
    print(f"  State disagrees with later activity: {sum(item['state_mismatch'] for item in states)} of {len(states)} tools")

    parts = part_summary(kept)
    print(f"\nPart families ({parts['total_scans']} scans, {parts['distinct_labels']} spellings, {len(parts['families'])} families):")
    for item in parts["families"]:
        print(f"  {item['part']:<7s}: {item['scans']:2d} scans, {item['distinct_spellings']:2d} spellings")

    print("\nEnergy windows (net=0):")
    for item in energy_summary(kept):
        print(
            f"  {item['tool_id']}: {item['slots']} slots, net={item['net_energy']:2d}, "
            f"zero_windows={item['zero_windows']}"
        )


if __name__ == "__main__":
    main(*sys.argv[1:])
