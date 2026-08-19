import pytest

def test_missing_dict_key_108():
    config = {"timeout": 30, "retries": 3}
    val = config["missing_key_4967"]
    assert val == True
