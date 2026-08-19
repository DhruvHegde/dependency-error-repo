import pytest

def test_missing_dict_key_4():
    config = {"timeout": 30, "retries": 3}
    val = config["missing_key_9890"]
    assert val == True
