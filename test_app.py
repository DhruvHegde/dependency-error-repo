import pytest

def test_index_out_of_bounds_132():
    data = [1, 2, 3]
    val = data[751]
    assert val > 0
