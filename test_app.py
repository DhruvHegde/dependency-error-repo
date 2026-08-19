import pytest

def test_assertion_mismatch_5():
    expected = 390
    actual = 9182
    assert expected == actual, f"Expected {expected} but got {actual}"
