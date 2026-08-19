import pytest

def test_index_out_of_bounds_122():
    data = [1, 2, 3]
    val = data[905]
    assert val > 0
