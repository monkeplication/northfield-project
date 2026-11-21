from solutions import latest_state


def test_out_of_order_events():
    events = [
        ("NT-101", "2026-11-02 12:00:00", "RUNNING"),
        ("NT-101", "2026-11-02 09:00:00", "IDLE"),
        ("NT-102", "2026-11-02 08:00:00", "OVERLOAD"),
        ("NT-102", "2026-11-02 16:30:00", "IDLE"),
    ]
    assert latest_state(events) == {"NT-101": "RUNNING", "NT-102": "IDLE"}


def test_empty_input():
    assert latest_state([]) == {}


def test_missing_timestamp_ignored():
    events = [
        ("NT-101", "2026-11-02 09:00:00", "RUNNING"),
        ("NT-101", "", "OVERHEATED"),
        ("NT-101", None, "LOW_BATTERY"),
        ("NT-102", "", "IDLE"),
    ]
    assert latest_state(events) == {"NT-101": "RUNNING"}


def test_calls_are_independent():
    first = latest_state([("NT-101", "2026-11-02 09:00:00", "RUNNING")])
    second = latest_state([("NT-102", "2026-11-02 10:00:00", "IDLE")])
    assert first == {"NT-101": "RUNNING"}
    assert second == {"NT-102": "IDLE"}


def test_same_timestamp_later_event_wins():
    events = [
        ("NT-101", "2026-11-02 09:00:00", "RUNNING"),
        ("NT-101", "2026-11-02 09:00:00", "OVERLOAD"),
    ]
    assert latest_state(events) == {"NT-101": "OVERLOAD"}


def test_multiple_tools_mixed_order():
    events = [
        ("NT-103", "2026-11-02 12:52:00", "OVERHEATED"),
        ("NT-104", "2026-11-02 08:15:00", "RUNNING"),
        ("NT-103", "2026-11-02 09:10:00", "IDLE"),
        ("NT-104", "2026-11-02 13:24:00", "IDLE"),
        ("NT-105", "2026-11-02 10:51:00", "RUNNING"),
    ]
    assert latest_state(events) == {
        "NT-103": "OVERHEATED",
        "NT-104": "IDLE",
        "NT-105": "RUNNING",
    }
