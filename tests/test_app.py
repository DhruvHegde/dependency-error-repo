import pytest
from src.app import (
    calculate_division,
    convert_to_int,
    get_list_item,
    get_dict_value,
    assert_positive
)

def test_calculate_division():
    assert calculate_division(10, 2) == 5.0

def test_convert_to_int():
    assert convert_to_int("42") == 42

def test_get_list_item():
    assert get_list_item([1, 2, 3], 1) == 2

def test_get_dict_value():
    assert get_dict_value({"a": 1}, "a") == 1

def test_assert_positive():
    assert assert_positive(5) == 5


# --- SYNTHETIC F3 FAILURE MUTATION ---

def test_zero_division_error():
    """Injected synthetic ZeroDivisionError."""
    from src.app import calculate_division
    calculate_division(42, 0)
