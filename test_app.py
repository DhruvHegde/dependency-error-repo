import pytest

def test_assertion_mismatch_50():
    expected = 455
    actual = 7214
    assert expected == actual, f"Expected {expected} but got {actual}"
