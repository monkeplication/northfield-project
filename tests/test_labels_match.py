import pytest

from solutions import labels_match


@pytest.mark.parametrize(
    "a, b, expected",
    [
        ("socket", "ktesco", True),
        ("rebar", "brace", False),
        ("torque", "torques", False),
        ("a", "a", True),
        ("aab", "abb", False),
        ("ab", "ba", True),
    ],
)
def test_examples_and_edges(a, b, expected):
    assert labels_match(a, b) is expected


def test_empty_labels():
    assert labels_match("", "") is True
    assert labels_match("", "a") is False


def test_single_substitution():
    assert labels_match("abcdefghijklmnopqrstuvwxy", "abcdefghijklmnopqrstuvwxz") is False
