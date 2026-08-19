import pytest

def test_assertion_mismatch_3():
    expected = 987
    actual = 6539
    assert expected == actual, f"Expected {expected} but got {actual}"
