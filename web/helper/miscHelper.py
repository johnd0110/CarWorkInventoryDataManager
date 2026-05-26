from typing import Any
from argparse import ArgumentError

def replace_dict_empty_string_vals_with_none(dictToModify: dict[str, Any]):
    return {key: (None if val == '' else val) for key, val in dictToModify.items()}


def addItemToDictionary(dictionary, key, value):
    key = key.lower()
    if key in dictionary:
        raise ArgumentError(message="Duplicate key found")
    else:
        dictionary[key] = value