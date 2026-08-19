import pytest

def test_assertion_mismatch_43():
    expected = 849
    actual = 5516
    assert expected == actual, f"Expected {expected} but got {actual}"
