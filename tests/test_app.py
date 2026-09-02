import pytest
from src.app import get_list_item

def test_get_list_item():
    assert get_list_item([1, 2, 3], 999) == 2
