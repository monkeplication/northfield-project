from solutions import group_families


def normalise(groups):
    return sorted(sorted(group) for group in groups)


def test_scrambled_labels():
    codes = ["rebar", "brace", "arebr", "cebar", "socket", "rabre"]
    expected = [["rebar", "arebr", "rabre"], ["brace", "cebar"], ["socket"]]
    assert normalise(group_families(codes)) == normalise(expected)


def test_empty_codes():
    assert group_families([""]) == [[""]]
    assert normalise(group_families(["", "", "a"])) == [["", ""], ["a"]]


def test_repeated_code_kept():
    assert group_families(["drill", "drill"]) == [["drill", "drill"]]


def test_different_counts_separate():
    assert normalise(group_families(["aab", "abb", "bab"])) == [["aab"], ["abb", "bab"]]
