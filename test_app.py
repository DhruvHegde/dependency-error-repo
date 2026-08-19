import pytest

def test_type_mismatch_59():
    result = "string_value" + 149
    assert result is not None
