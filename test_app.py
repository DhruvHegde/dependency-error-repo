import pytest

def test_missing_dict_key_142():
    config = {"timeout": 30, "retries": 3}
    val = config["missing_key_1362"]
    assert val == True
