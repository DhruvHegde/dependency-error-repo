import pytest

def test_type_mismatch_51():
    result = "string_value" + 518
    assert result is not None
