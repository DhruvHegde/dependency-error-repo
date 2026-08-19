import pytest

def test_missing_dict_key_10():
    config = {"timeout": 30, "retries": 3}
    val = config["missing_key_2550"]
    assert val == True
