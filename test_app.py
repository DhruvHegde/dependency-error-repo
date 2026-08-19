import pytest

def test_missing_dict_key_70():
    config = {"timeout": 30, "retries": 3}
    val = config["missing_key_7230"]
    assert val == True
