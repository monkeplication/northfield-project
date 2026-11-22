from collections import Counter

from fleet_findings import (
    DATA,
    clean_events,
    energy_summary,
    fault_summary,
    load_events,
    part_summary,
    state_summary,
    usage_summary,
)


def test_cleaning_counts():
    kept, removed = clean_events(load_events(DATA))
    assert len(kept) == 246
    assert Counter(reason for reason, _ in removed) == {
        "duplicate": 8,
        "missing timestamp": 1,
        "outside reporting day": 1,
    }


def test_cleaning_keeps_first_copy_of_duplicate():
    row = {
        "event_id": "EV1",
        "tool_id": "NT-1",
        "timestamp": "2026-11-02 09:00:00",
        "state": "IDLE",
        "part_label": "",
        "fault_code": "",
        "net_energy": "",
        "session_start_min": "",
        "session_end_min": "",
    }
    kept, removed = clean_events([row, dict(row), dict(row, state="RUNNING")])
    assert kept == [row]
    assert [reason for reason, _ in removed] == ["duplicate", "conflicting duplicate"]


def test_usage_totals():
    kept, _ = clean_events(load_events(DATA))
    usage = usage_summary(kept)
    assert usage["totals"] == {
        "sessions": 56,
        "raw_minutes": 2613,
        "merged_minutes": 2160,
        "double_counted": 453,
    }


def test_fault_top_k_includes_tie():
    kept, _ = clean_events(load_events(DATA))
    faults = fault_summary(kept, k=3)
    assert faults["total"] == 26
    top_codes = [item["code"] for item in faults["codes"] if item["in_top_k"]]
    assert top_codes == [205, 101, 620, 518]


def test_state_safety_and_stale_idle():
    kept, _ = clean_events(load_events(DATA))
    by_tool = {item["tool_id"]: item for item in state_summary(kept)}
    safety_tools = {t for t, item in by_tool.items() if item["is_safety"]}
    assert safety_tools == {"NT-103", "NT-110", "NT-111"}
    assert by_tool["NT-106"]["state"] == "IDLE"
    assert by_tool["NT-106"]["events_after"] == 9
    assert by_tool["NT-106"]["sessions_after"] == 2


def test_state_mismatch():
    kept, _ = clean_events(load_events(DATA))
    mismatched = {item["tool_id"] for item in state_summary(kept) if item["state_mismatch"]}
    assert mismatched == {"NT-103", "NT-106", "NT-111", "NT-112"}


def test_part_families_and_energy():
    kept, _ = clean_events(load_events(DATA))
    parts = part_summary(kept)
    assert parts["total_scans"] == 64
    assert len(parts["families"]) == 8

    energy = {item["tool_id"]: item for item in energy_summary(kept)}
    assert sum(item["zero_windows"] for item in energy.values()) == 4
