import pytest

def test_assertion_mismatch_106():
    expected = 460
    actual = 5879
    assert expected == actual, f"Expected {expected} but got {actual}"
