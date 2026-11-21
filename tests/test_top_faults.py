from solutions import top_faults


def test_examples():
    assert sorted(top_faults([620, 205, 205, 101, 620, 205], 2)) == [205, 620]
    assert top_faults([412], 1) == [412]
    assert top_faults([-3, 7, -3, 7, -3], 1) == [-3]


def test_k_equals_distinct_count():
    assert sorted(top_faults([1, 2, 2, 3, 3, 3], 3)) == [1, 2, 3]


def test_negative_and_zero_codes():
    assert sorted(top_faults([0, -1, 0, -1, 5], 2)) == [-1, 0]


def test_tied_counts_below_top_one():
    result = top_faults([9, 9, 9, 9, 1, 1, 2, 2, 3, 3], 2)
    assert result[0] == 9
    assert len(result) == 2


def test_large_batch():
    codes = list(range(100_000)) + [42, 42, 42, -7, -7]
    assert sorted(top_faults(codes, 2)) == [-7, 42]
