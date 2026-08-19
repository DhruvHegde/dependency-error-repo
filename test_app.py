import pytest

def test_index_out_of_bounds_81():
    data = [1, 2, 3]
    val = data[956]
    assert val > 0
