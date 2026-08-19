import pytest

def test_index_out_of_bounds_99():
    data = [1, 2, 3]
    val = data[448]
    assert val > 0
