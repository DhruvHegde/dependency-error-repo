import pytest

def test_assertion_mismatch_27():
    expected = 711
    actual = 3286
    assert expected == actual, f"Expected {expected} but got {actual}"
