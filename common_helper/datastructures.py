from collections import UserDict
from typing import Any

class lowerCaseKeyDict(UserDict):
    def __init__(self, aDictionary: dict[str, Any] = {}):
        super().__init__()
        self.data = {key.lower(): value for key, value in aDictionary.items()}

    def __getitem__(self, key: str):
        lowerKey = key.lower()
        if lowerKey not in self.data: raise KeyError(lowerKey)
        return self.data[lowerKey]

    def __contains__(self, key: str):
        return key.lower() in self.data

    def __setitem__(self, key, value):
        self.data[key.lower()] = value

    def __delitem__(self, key: str):
        del self.data[key.lower()]