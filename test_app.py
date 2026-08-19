import pytest

def test_assertion_mismatch_41():
    expected = 102
    actual = 5029
    assert expected == actual, f"Expected {expected} but got {actual}"
