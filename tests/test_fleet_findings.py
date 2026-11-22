from collections import Counter

from fleet_findings import DATA, clean_events, fault_summary, load_events, usage_summary


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
