import pytest

def test_missing_dict_key_107():
    config = {"timeout": 30, "retries": 3}
    val = config["missing_key_5074"]
    assert val == True
