import pytest

def test_type_mismatch_128():
    result = "string_value" + 351
    assert result is not None
