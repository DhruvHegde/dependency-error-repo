import pytest

def test_type_mismatch_19():
    result = "string_value" + 317
    assert result is not None
