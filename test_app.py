import time

def test_timeout_473():
    counter = 510
    while counter != 266337:
        counter += 1
