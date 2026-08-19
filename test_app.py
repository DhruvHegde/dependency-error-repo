import pytest

def test_type_mismatch_49():
    result = "string_value" + 837
    assert result is not None
