import pytest

def test_missing_dict_key_34():
    config = {"timeout": 30, "retries": 3}
    val = config["missing_key_8676"]
    assert val == True
