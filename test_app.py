import pytest

def test_index_out_of_bounds_2():
    data = [1, 2, 3]
    val = data[467]
    assert val > 0
