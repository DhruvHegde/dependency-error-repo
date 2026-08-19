import pytest

def test_missing_dict_key_127():
    config = {"timeout": 30, "retries": 3}
    val = config["missing_key_2518"]
    assert val == True
