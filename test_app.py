import pytest

def test_type_mismatch_14():
    result = "string_value" + 241
    assert result is not None
