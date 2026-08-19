import pytest

def test_missing_dict_key_73():
    config = {"timeout": 30, "retries": 3}
    val = config["missing_key_2444"]
    assert val == True
