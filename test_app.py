import pytest

def test_index_out_of_bounds_117():
    data = [1, 2, 3]
    val = data[694]
    assert val > 0
