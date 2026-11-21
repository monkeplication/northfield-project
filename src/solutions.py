from collections import defaultdict


def labels_match(a: str, b: str) -> bool:
    """Return True if b is a rearrangement of a."""
    return len(a) == len(b) and sorted(a) == sorted(b)


def group_families(codes: list[str]) -> list[list[str]]:
    """Group part codes that are rearrangements of each other."""
    families: dict[tuple[str, ...], list[str]] = defaultdict(list)
    for code in codes:
        families[tuple(sorted(code))].append(code)
    return list(families.values())
