import pytest

def test_assertion_mismatch_42():
    expected = 196
    actual = 6113
    assert expected == actual, f"Expected {expected} but got {actual}"
