import pytest

def test_index_out_of_bounds_58():
    data = [1, 2, 3]
    val = data[410]
    assert val > 0
