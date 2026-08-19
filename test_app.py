import pytest

def test_assertion_mismatch_103():
    expected = 183
    actual = 9841
    assert expected == actual, f"Expected {expected} but got {actual}"
