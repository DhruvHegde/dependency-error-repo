import pytest

def test_index_out_of_bounds_46():
    data = [1, 2, 3]
    val = data[420]
    assert val > 0
