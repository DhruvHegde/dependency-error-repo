import pytest

def test_index_out_of_bounds_57():
    data = [1, 2, 3]
    val = data[234]
    assert val > 0
