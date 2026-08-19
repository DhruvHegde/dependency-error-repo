import pytest

def test_assertion_mismatch_111():
    expected = 670
    actual = 2550
    assert expected == actual, f"Expected {expected} but got {actual}"
