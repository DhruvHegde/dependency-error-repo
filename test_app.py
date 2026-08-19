import pytest

def test_index_out_of_bounds_21():
    data = [1, 2, 3]
    val = data[370]
    assert val > 0
