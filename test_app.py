import pytest

def test_index_out_of_bounds_101():
    data = [1, 2, 3]
    val = data[920]
    assert val > 0
