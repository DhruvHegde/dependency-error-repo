import pytest

def test_missing_dict_key_124():
    config = {"timeout": 30, "retries": 3}
    val = config["missing_key_1970"]
    assert val == True
