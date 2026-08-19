import pytest

def test_type_mismatch_41():
    result = "string_value" + 585
    assert result is not None
