import pytest

def test_missing_dict_key_96():
    config = {"timeout": 30, "retries": 3}
    val = config["missing_key_3144"]
    assert val == True
