import pytest

from solutions import merge_sessions


@pytest.mark.parametrize(
    "sessions, expected",
    [
        ([[300, 340], [310, 360], [400, 420]], [[300, 360], [400, 420]]),
        ([[100, 500], [150, 200], [300, 350]], [[100, 500]]),
        ([[50, 80], [10, 20], [20, 30]], [[10, 30], [50, 80]]),
        ([[10, 20], [30, 40]], [[10, 20], [30, 40]]),
    ],
)
def test_examples_and_edges(sessions, expected):
    assert merge_sessions(sessions) == expected


def test_touching_sessions_merge():
    assert merge_sessions([[60, 90], [90, 120]]) == [[60, 120]]


def test_zero_length_session():
    assert merge_sessions([[5, 5]]) == [[5, 5]]


def test_contained_session():
    assert merge_sessions([[0, 1_000_000], [0, 0]]) == [[0, 1_000_000]]


def test_long_chain_of_touching_sessions():
    sessions = [[i * 5, (i + 1) * 5] for i in range(1_000)]
    assert merge_sessions(sessions) == [[0, 5_000]]


def test_large_disjoint_sessions():
    n = 100_000
    sessions = [[i * 10, i * 10 + 5] for i in range(n)][::-1]
    merged = merge_sessions(sessions)
    assert len(merged) == n
    assert merged[0] == [0, 5]
    assert merged[-1] == [(n - 1) * 10, (n - 1) * 10 + 5]


def test_large_overlapping_sessions():
    sessions = [[i, 1_000_000 - i] for i in range(100_000)]
    assert merge_sessions(sessions) == [[0, 1_000_000]]
