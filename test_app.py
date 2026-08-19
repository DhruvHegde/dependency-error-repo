import pytest

def test_index_out_of_bounds_68():
    data = [1, 2, 3]
    val = data[232]
    assert val > 0
