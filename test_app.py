import pytest

def test_type_mismatch_15():
    result = "string_value" + 369
    assert result is not None
