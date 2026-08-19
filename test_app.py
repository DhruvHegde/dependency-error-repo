import pytest

def test_index_out_of_bounds_93():
    data = [1, 2, 3]
    val = data[219]
    assert val > 0
