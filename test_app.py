import pytest

def test_assertion_mismatch_54():
    expected = 669
    actual = 1744
    assert expected == actual, f"Expected {expected} but got {actual}"
