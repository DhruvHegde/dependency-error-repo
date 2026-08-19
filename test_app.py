import pytest

def test_missing_dict_key_53():
    config = {"timeout": 30, "retries": 3}
    val = config["missing_key_5630"]
    assert val == True
