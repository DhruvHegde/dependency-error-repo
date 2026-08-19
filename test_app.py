import pytest

def test_assertion_mismatch_63():
    expected = 189
    actual = 2127
    assert expected == actual, f"Expected {expected} but got {actual}"
