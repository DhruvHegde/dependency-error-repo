import pytest

def test_index_out_of_bounds_59():
    data = [1, 2, 3]
    val = data[802]
    assert val > 0
