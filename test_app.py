import pytest

def test_index_out_of_bounds_115():
    data = [1, 2, 3]
    val = data[278]
    assert val > 0
