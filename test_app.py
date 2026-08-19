import pytest

def test_assertion_mismatch_60():
    expected = 909
    actual = 5743
    assert expected == actual, f"Expected {expected} but got {actual}"
