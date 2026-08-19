import pytest

def test_index_out_of_bounds_3():
    data = [1, 2, 3]
    val = data[456]
    assert val > 0
