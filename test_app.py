import pytest

def test_assertion_mismatch_66():
    expected = 508
    actual = 8701
    assert expected == actual, f"Expected {expected} but got {actual}"
