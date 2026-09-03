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

# Trigger batch 1 at 1788459479.4771721

# Trigger batch 1 at 1788459557.6447065

# Trigger batch 1 at 1788459605.3949118

# Trigger batch 1 at 1788460284.694471

# Trigger batch 1 at 1788460587.7853956

# Trigger batch 1 at 1788461037.2812247

# Trigger batch 1 at 1788461132.8240862

# Trigger batch 1 at 1788461794.2201023
