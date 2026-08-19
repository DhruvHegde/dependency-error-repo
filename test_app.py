import pytest

def test_assertion_mismatch_80():
    expected = 709
    actual = 6407
    assert expected == actual, f"Expected {expected} but got {actual}"
