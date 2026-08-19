import pytest

def test_missing_dict_key_65():
    config = {"timeout": 30, "retries": 3}
    val = config["missing_key_6987"]
    assert val == True
