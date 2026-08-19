import pytest

def test_assertion_mismatch_58():
    expected = 149
    actual = 4839
    assert expected == actual, f"Expected {expected} but got {actual}"
