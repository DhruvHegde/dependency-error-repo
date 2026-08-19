import pytest

def test_assertion_mismatch_7():
    expected = 233
    actual = 6901
    assert expected == actual, f"Expected {expected} but got {actual}"
