import pytest

def test_assertion_mismatch_129():
    expected = 761
    actual = 6680
    assert expected == actual, f"Expected {expected} but got {actual}"
