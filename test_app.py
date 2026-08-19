import pytest

def test_assertion_mismatch_30():
    expected = 534
    actual = 5709
    assert expected == actual, f"Expected {expected} but got {actual}"
