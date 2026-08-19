import pytest

def test_assertion_mismatch_61():
    expected = 973
    actual = 1976
    assert expected == actual, f"Expected {expected} but got {actual}"
