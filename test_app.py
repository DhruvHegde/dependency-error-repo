import pytest

def test_assertion_mismatch_119():
    expected = 295
    actual = 3954
    assert expected == actual, f"Expected {expected} but got {actual}"
