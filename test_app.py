import pytest

def test_index_out_of_bounds_45():
    data = [1, 2, 3]
    val = data[298]
    assert val > 0
