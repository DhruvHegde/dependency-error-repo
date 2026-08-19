import pytest

def test_assertion_mismatch_8():
    expected = 592
    actual = 1173
    assert expected == actual, f"Expected {expected} but got {actual}"
