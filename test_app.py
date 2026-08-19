import pytest

def test_type_mismatch_90():
    result = "string_value" + 138
    assert result is not None
