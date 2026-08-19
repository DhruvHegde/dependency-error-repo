import pytest

def test_missing_dict_key_48():
    config = {"timeout": 30, "retries": 3}
    val = config["missing_key_1444"]
    assert val == True
