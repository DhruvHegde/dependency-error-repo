import pytest

def test_type_mismatch_134():
    result = "string_value" + 571
    assert result is not None
