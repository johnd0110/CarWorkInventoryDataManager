from collections.abc import MutableMapping
from typing import Any

class lowerCaseKeyDict(MutableMapping):
    def __init__(self, aDictionary: dict[str, Any] = {}):
        self.lowercaseKeyDict = {key.lower(): value for key, value in aDictionary.items()}

    def __getitem__(self, key: str):
        lowerKey = key.lower()
        if lowerKey not in self.lowercaseKeyDict: raise KeyError(lowerKey)
        return self.lowercaseKeyDict[lowerKey]

    def __setitem__(self, key, value):
        self.lowercaseKeyDict[key.lower()] = value

    def __len__(self):
        return len(self.lowercaseKeyDict)

    def __iter__(self):
        return iter(self.lowercaseKeyDict)

    def __delitem__(self, key: str):
        del self.lowercaseKeyDict[key.lower()]

    def __str__(self):
        return str(self.lowercaseKeyDict)