import pytest

def test_type_mismatch_53():
    result = "string_value" + 411
    assert result is not None
