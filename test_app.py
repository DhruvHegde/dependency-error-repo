import pytest

def test_type_mismatch_116():
    result = "string_value" + 633
    assert result is not None
