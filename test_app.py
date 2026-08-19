import pytest

def test_index_out_of_bounds_148():
    data = [1, 2, 3]
    val = data[928]
    assert val > 0
