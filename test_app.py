import pytest

def test_assertion_mismatch_47():
    expected = 693
    actual = 2276
    assert expected == actual, f"Expected {expected} but got {actual}"
