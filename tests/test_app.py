import pytest
from src.app import assert_positive

def test_assert_positive():
    assert assert_positive(-5) == -5
