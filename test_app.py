import pytest

def test_assertion_mismatch_147():
    expected = 552
    actual = 6319
    assert expected == actual, f"Expected {expected} but got {actual}"
