"""Custom global functions."""


def set_nested_item(_dict: dict, path: list[str], val):
    """
    Update value in nested dictionary.
    
    :Example: set_nested_item(d, ["key_1", "key_2", "key_3"], value)
    
    :param _dict: dict in which the value should be updated
    :param path: list of keys to the value in data_dict
    :param val: new value to update old value with
    
    :returns: data_dict with updated value
    """
    from functools import reduce
    from operator import getitem

    reduce(getitem, path[:-1], _dict)[path[-1]] = val
    return _dict


def check_last_character(string):
    """Check if the last char of string, or a list of strings, is '/'. If not, add one."""
    if isinstance(string, str):
        return string if string[-1] == "/" else f"{string}/"
    else:
        return [s if s[-1] == "/" else f"{s}/" for s in string]


def deep_get(_dict, keys, default=None):
    """Get value from a key in a nested dictionary"""
    for key in keys:
        if isinstance(_dict, dict):
            _dict = _dict.get(key, default)
        else:
            return default
    return _dict


def unpack(packed_list, steps=0):
    """Unpack single/multiple element/-s in n-packed list"""

    # n-packed list with multiple elements
    if steps > 0:
        [element] = packed_list
        for _ in range(steps - 1):
            [element] = element
        return element

    # n-packed list with one element
    [element] = packed_list
    while type(element) == list:
        [element] = element  # double list
    return element


def create_pair_dict(list):
    """Create from a list a dictionary with pairs of two"""
    data, steps = {}, 2

    for i in range(0, len(list) - 1, steps):
        key, value = list[i:i + steps]
        data[key] = value

    return data


def unpack_tuple_list(tuple_list):
    """Create a list from a list of tuples"""
    _ = []
    for k, v in tuple_list:
        _ += [k, v]
    return _
