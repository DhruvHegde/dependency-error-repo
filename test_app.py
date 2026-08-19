import pytest

def test_type_mismatch_83():
    result = "string_value" + 437
    assert result is not None
