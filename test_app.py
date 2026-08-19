import pytest

def test_index_out_of_bounds_126():
    data = [1, 2, 3]
    val = data[379]
    assert val > 0
