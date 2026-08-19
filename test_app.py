import pytest

def test_index_out_of_bounds_48():
    data = [1, 2, 3]
    val = data[859]
    assert val > 0
