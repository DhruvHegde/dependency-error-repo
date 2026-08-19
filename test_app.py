import pytest

def test_type_mismatch_66():
    result = "string_value" + 248
    assert result is not None
