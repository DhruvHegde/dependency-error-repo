import pytest

def test_type_mismatch_94():
    result = "string_value" + 491
    assert result is not None
