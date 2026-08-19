import pytest

def test_type_mismatch_104():
    result = "string_value" + 958
    assert result is not None
