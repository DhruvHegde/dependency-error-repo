import pytest

def test_missing_dict_key_15():
    config = {"timeout": 30, "retries": 3}
    val = config["missing_key_5220"]
    assert val == True
