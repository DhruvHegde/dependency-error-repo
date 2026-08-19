import pytest

def test_index_out_of_bounds_91():
    data = [1, 2, 3]
    val = data[364]
    assert val > 0
