import pytest

def test_type_mismatch_137():
    result = "string_value" + 123
    assert result is not None
