import pytest

def test_assertion_mismatch_110():
    expected = 775
    actual = 7413
    assert expected == actual, f"Expected {expected} but got {actual}"
