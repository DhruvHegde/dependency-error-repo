def calculate_division(a, b):
    return a / b

def convert_to_int(val):
    return int(val)

def get_list_item(lst, index):
    return lst[index]

def get_dict_value(d, key):
    return d[key]

def get_object_attribute(obj):
    return obj.non_existent_attribute

def read_config_file(path):
    with open(path, "r") as f:
        return f.read()

def assert_positive(n):
    assert n > 0, "Number must be positive"
    return n
