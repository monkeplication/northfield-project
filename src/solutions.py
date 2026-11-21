import heapq
from collections import Counter, defaultdict


def _letter_counts(text: str) -> tuple[int, ...]:
    counts = [0] * 26
    for ch in text:
        counts[ord(ch) - ord("a")] += 1
    return tuple(counts)


def labels_match(a: str, b: str) -> bool:
    """Return True if b is a rearrangement of a."""
    return len(a) == len(b) and _letter_counts(a) == _letter_counts(b)


def group_families(codes: list[str]) -> list[list[str]]:
    """Group part codes that are rearrangements of each other."""
    families: dict[tuple[int, ...], list[str]] = defaultdict(list)
    for code in codes:
        families[_letter_counts(code)].append(code)
    return list(families.values())


def count_windows(readings: list[int], k: int) -> int:
    """Count contiguous subarrays whose elements sum to k."""
    seen = {0: 1}
    total = 0
    windows = 0
    for reading in readings:
        total += reading
        windows += seen.get(total - k, 0)
        seen[total] = seen.get(total, 0) + 1
    return windows


def top_faults(codes: list[int], k: int) -> list[int]:
    """Return the k most frequent fault codes."""
    counts = Counter(codes)
    return heapq.nlargest(k, counts, key=counts.__getitem__)


def merge_sessions(sessions: list[list[int]]) -> list[list[int]]:
    """Merge overlapping or touching [start, end] sessions."""
    merged: list[list[int]] = []
    for start, end in sorted(sessions):
        if merged and start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return merged


def latest_state(events: list[tuple]) -> dict[str, str]:
    """Return each tool's most recent state (later arrival wins on equal timestamps)."""
    latest: dict[str, tuple[str, str]] = {}
    for tool_id, ts, state in events:
        if not ts:
            continue
        if tool_id not in latest or ts >= latest[tool_id][0]:
            latest[tool_id] = (ts, state)
    return {tool_id: state for tool_id, (_, state) in latest.items()}
