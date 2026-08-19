import pytest

def test_assertion_mismatch_40():
    expected = 115
    actual = 1500
    assert expected == actual, f"Expected {expected} but got {actual}"
