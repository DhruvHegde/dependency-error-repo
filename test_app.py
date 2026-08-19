import pytest

def test_type_mismatch_131():
    result = "string_value" + 894
    assert result is not None
