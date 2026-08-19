import pytest

def test_assertion_mismatch_22():
    expected = 214
    actual = 3288
    assert expected == actual, f"Expected {expected} but got {actual}"
