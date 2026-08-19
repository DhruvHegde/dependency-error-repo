import pytest

def test_type_mismatch_50():
    result = "string_value" + 155
    assert result is not None
