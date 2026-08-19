import pytest

def test_assertion_mismatch_118():
    expected = 367
    actual = 6628
    assert expected == actual, f"Expected {expected} but got {actual}"
