import pytest

def test_type_mismatch_125():
    result = "string_value" + 110
    assert result is not None
