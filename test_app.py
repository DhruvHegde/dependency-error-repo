import pytest

def test_index_out_of_bounds_32():
    data = [1, 2, 3]
    val = data[828]
    assert val > 0
