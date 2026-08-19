import pytest

def test_type_mismatch_38():
    result = "string_value" + 264
    assert result is not None
