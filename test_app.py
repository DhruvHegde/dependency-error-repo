import pytest

def test_type_mismatch_57():
    result = "string_value" + 966
    assert result is not None
