import pytest

def test_index_out_of_bounds_77():
    data = [1, 2, 3]
    val = data[150]
    assert val > 0
