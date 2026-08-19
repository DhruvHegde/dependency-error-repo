import pytest

def test_index_out_of_bounds_23():
    data = [1, 2, 3]
    val = data[107]
    assert val > 0
