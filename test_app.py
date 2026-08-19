import pytest

def test_assertion_mismatch_37():
    expected = 778
    actual = 1704
    assert expected == actual, f"Expected {expected} but got {actual}"
