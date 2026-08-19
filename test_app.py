import pytest

def test_index_out_of_bounds_25():
    data = [1, 2, 3]
    val = data[997]
    assert val > 0
