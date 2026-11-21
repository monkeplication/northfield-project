import heapq
from collections import Counter, defaultdict


def labels_match(a: str, b: str) -> bool:
    """Return True if b is a rearrangement of a."""
    return len(a) == len(b) and sorted(a) == sorted(b)


def group_families(codes: list[str]) -> list[list[str]]:
    """Group part codes that are rearrangements of each other."""
    families: dict[tuple[str, ...], list[str]] = defaultdict(list)
    for code in codes:
        families[tuple(sorted(code))].append(code)
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
