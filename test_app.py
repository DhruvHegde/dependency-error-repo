import pytest

def test_assertion_mismatch_38():
    expected = 982
    actual = 4085
    assert expected == actual, f"Expected {expected} but got {actual}"
