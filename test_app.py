import pytest

def test_assertion_mismatch_76():
    expected = 146
    actual = 1903
    assert expected == actual, f"Expected {expected} but got {actual}"
