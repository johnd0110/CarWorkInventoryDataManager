import sqlite3
from argparse import ArgumentError
from dataclasses import dataclass
from collections.abc import MutableMapping
from typing import Any
from itertools import groupby

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

@dataclass
class columnWebAttributes:
    dropDownData: tuple[str, list] = None
    visibility: str = "initial"
    canBeInput: bool = False
    requiredInput: bool = False
    nestedOn: bool = False
    nestPriority: int = -1

class columnNamesAndAttributes(lowerCaseKeyDict):
    def __init__(self, *args):
        super().__init__(*args)

    def getColumnsToNestOnOrderedByPriority(self):
        """
        Retrieves all column names with the web attribute nestedOn = True and sorts them in descending order by their assigned priority (Higher Value = Higher Priority)
        Then the columnNames are grouped by the priority value.
        :return: A list of tuples representing the grouped column names by priority, in order by priority and a plain list of all the columns with the nestedOn attribute = True
        """
        result = sorted([(columnName, attributes.nestPriority) for columnName, attributes in self.lowercaseKeyDict.items() if attributes.nestedOn], key=lambda x: x[1], reverse=True)
        return [tuple([column[0] for column in group]) for _, group in groupby(result, lambda x: x[1])], [columnNameAttr[0] for columnNameAttr in result]

class baseSQL:
    def __init__(self, databaseName=":memory:", rowFactory=sqlite3.Row):
        self.connection = sqlite3.connect(databaseName)
        self.connection.row_factory = rowFactory
        # Must explicitly enable foreign keys for sqlite
        _ = self.executeAndCommitSQLStatement("PRAGMA foreign_keys=ON")

    def executeAndCommitSQLStatement(self, SQLStatement: str, placeholderValues: tuple = (), returnColumnNames = False, IsScript=False) -> tuple[list, columnNamesAndAttributes]:
        """
        Creates a cursor and then executes a sql statement with the provided placeholder values
        then commits and cleans up the cursor
        :param SQLStatement: A SQL statement to execute. If IsScript is True, then this is assumed to be a script.
        :param placeholderValues: Values for the placeholders in the statement. If IsScript is True, then this does nothing.
        :param returnColumnNames: Return column names from the query that was run, may be empty. If IsScript is True, the returned column names may not be usable info or empty.
        :return: The result of the execute statement which may be the result set for a SELECT query or nothing useful for other queries like INSERT
        """
        cursor = self.connection.cursor()
        result = cursor.execute(SQLStatement, placeholderValues).fetchall() if not IsScript else cursor.executescript(SQLStatement)
        self.connection.commit()
        if returnColumnNames:
            columnNamesAndAttrs = columnNamesAndAttributes({colTuple[0]: columnWebAttributes() for colTuple in cursor.description})
            returnresult = (result, columnNamesAndAttrs)
        else:
            returnresult = (result, None)
        cursor.close()
        return returnresult

    def addSQLPlaceholderToString(self, stringToBeModified: str, numOfPlaceholders=1, closeString=True):
        """
        Adds numOfPlaceHolders SQL Placeholders to string.
        :param stringToBeModified: String to append SQL Placeholders to
        :param numOfPlaceholders: Number of placeholders to append, defaults to 1
        :param closeString: Add a closing parentheses to the string if true, defaults to true
        :return: String containing numOfPlaceholders placeholders
        """
        if numOfPlaceholders < 1:
            raise ArgumentError(message="Must be greater than 1.")

        for placeHolderNum in range(numOfPlaceholders):
            if placeHolderNum > 1:
                stringToBeModified += ", "
            stringToBeModified += "?"

        if closeString:
            stringToBeModified += ")"

        return stringToBeModified

    def cleanup(self):
        self.connection.close()

    @staticmethod
    def lowercaseKeyDictFactory(cursor, row):
        fields = [column[0] for column in cursor.description]
        return lowerCaseKeyDict({key: value for key, value in zip(fields, row)})


