import pytest

def test_assertion_mismatch_17():
    expected = 928
    actual = 7143
    assert expected == actual, f"Expected {expected} but got {actual}"
