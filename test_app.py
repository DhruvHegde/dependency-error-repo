import pytest

def test_assertion_mismatch_12():
    expected = 711
    actual = 1982
    assert expected == actual, f"Expected {expected} but got {actual}"
