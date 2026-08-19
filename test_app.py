import pytest

def test_missing_dict_key_47():
    config = {"timeout": 30, "retries": 3}
    val = config["missing_key_2367"]
    assert val == True
