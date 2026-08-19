import pytest

def test_assertion_mismatch_79():
    expected = 610
    actual = 8792
    assert expected == actual, f"Expected {expected} but got {actual}"
