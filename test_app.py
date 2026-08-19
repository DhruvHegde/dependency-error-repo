import pytest

def test_assertion_mismatch_62():
    expected = 159
    actual = 7816
    assert expected == actual, f"Expected {expected} but got {actual}"
