import pytest

def test_assertion_mismatch_34():
    expected = 424
    actual = 7216
    assert expected == actual, f"Expected {expected} but got {actual}"
