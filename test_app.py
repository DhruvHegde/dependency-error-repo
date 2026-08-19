import pytest

def test_type_mismatch_123():
    result = "string_value" + 326
    assert result is not None
