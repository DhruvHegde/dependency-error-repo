import pytest

def test_missing_dict_key_135():
    config = {"timeout": 30, "retries": 3}
    val = config["missing_key_4568"]
    assert val == True
