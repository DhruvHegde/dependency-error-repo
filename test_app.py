import pytest

def test_index_out_of_bounds_69():
    data = [1, 2, 3]
    val = data[623]
    assert val > 0
