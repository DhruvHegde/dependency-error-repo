import pytest

def test_type_mismatch_31():
    result = "string_value" + 978
    assert result is not None
