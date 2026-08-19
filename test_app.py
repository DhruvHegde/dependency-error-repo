import pytest

def test_index_out_of_bounds_109():
    data = [1, 2, 3]
    val = data[639]
    assert val > 0
