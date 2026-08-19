import pytest

def test_assertion_mismatch_43():
    expected = 438
    actual = 7839
    assert expected == actual, f"Expected {expected} but got {actual}"
