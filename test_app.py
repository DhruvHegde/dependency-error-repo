import pytest

def test_assertion_mismatch_84():
    expected = 902
    actual = 1767
    assert expected == actual, f"Expected {expected} but got {actual}"
