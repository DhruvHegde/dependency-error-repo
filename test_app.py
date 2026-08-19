import pytest

def test_assertion_mismatch_150():
    expected = 810
    actual = 9161
    assert expected == actual, f"Expected {expected} but got {actual}"
