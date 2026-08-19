import pytest

def test_index_out_of_bounds_20():
    data = [1, 2, 3]
    val = data[747]
    assert val > 0
