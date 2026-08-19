import pytest

def test_type_mismatch_27():
    result = "string_value" + 408
    assert result is not None
