import pytest

def test_assertion_mismatch_56():
    expected = 638
    actual = 3259
    assert expected == actual, f"Expected {expected} but got {actual}"
