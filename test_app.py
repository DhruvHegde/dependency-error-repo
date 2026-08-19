import pytest

def test_assertion_mismatch_7():
    expected = 534
    actual = 9992
    assert expected == actual, f"Expected {expected} but got {actual}"
