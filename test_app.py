import pytest

def test_assertion_mismatch_49():
    expected = 987
    actual = 4375
    assert expected == actual, f"Expected {expected} but got {actual}"
