import pytest

def test_missing_dict_key_2():
    config = {"timeout": 30, "retries": 3}
    val = config["missing_key_7155"]
    assert val == True
