import pytest

from solutions import count_windows


@pytest.mark.parametrize(
    "readings, k, expected",
    [
        ([1, 1, 1], 2, 2),
        ([2, -1, 1, 2], 2, 4),
        ([0, 0, 0], 0, 6),
        ([5], 5, 1),
        ([5], 3, 0),
    ],
)
def test_examples_and_edges(readings, k, expected):
    assert count_windows(readings, k) == expected


def test_negative_readings_and_target():
    assert count_windows([-1, -1, 1], -1) == 3
    assert count_windows([3, -2, -1], 0) == 1


def test_single_full_window():
    assert count_windows([1] * 10, 10) == 1
    assert count_windows([1] * 10, 11) == 0


def test_empty_input():
    assert count_windows([], 0) == 0


def test_large_zero_run():
    n = 100_000
    assert count_windows([0] * n, 0) == n * (n + 1) // 2
