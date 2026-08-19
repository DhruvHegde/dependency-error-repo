import pytest

def test_assertion_mismatch_88():
    expected = 773
    actual = 2413
    assert expected == actual, f"Expected {expected} but got {actual}"
