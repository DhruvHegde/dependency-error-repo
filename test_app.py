import pytest

def test_assertion_mismatch_60():
    expected = 221
    actual = 4357
    assert expected == actual, f"Expected {expected} but got {actual}"
