import pytest

def test_index_out_of_bounds_130():
    data = [1, 2, 3]
    val = data[678]
    assert val > 0
