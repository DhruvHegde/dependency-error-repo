import pytest

def test_index_out_of_bounds_14():
    data = [1, 2, 3]
    val = data[788]
    assert val > 0
