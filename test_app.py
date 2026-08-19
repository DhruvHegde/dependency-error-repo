import pytest

def test_missing_dict_key_140():
    config = {"timeout": 30, "retries": 3}
    val = config["missing_key_2644"]
    assert val == True
