import pytest

def test_assertion_mismatch_138():
    expected = 766
    actual = 1578
    assert expected == actual, f"Expected {expected} but got {actual}"
