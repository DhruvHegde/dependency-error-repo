import pytest

def test_assertion_mismatch_9():
    expected = 991
    actual = 1149
    assert expected == actual, f"Expected {expected} but got {actual}"
