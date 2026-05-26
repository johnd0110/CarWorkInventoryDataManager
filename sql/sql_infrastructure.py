import sqlite3
from argparse import ArgumentError

from common_helper import lowerCaseKeyDict

class columnNames:
    """
    General class for storing SQL column names
    Can be inherited from to provide a standard way to store and access SQL column names
    and is the expected class type for storing column names coming out of SQL queries from baseSQL classses
    """
    def __init__(self, sqlColumnNames: list[str]):
        """
        :param columnNames: list of column names to assign to self.columnNames
        """

        # Strip down the cursor description tuple down to just the column names in a list
        self.columnNames = sqlColumnNames

    @staticmethod
    def getColumnNamesListFromSqlCursorDescription(sqlresultcolumnnames: tuple[tuple[str, None, None, None, None, None, None]]) -> list[str]:
        return [colTuple[0] for colTuple in sqlresultcolumnnames]

class baseSQL:
    """Base Class for providing common SQL functionality"""
    def __init__(self, databaseName=":memory:", rowFactory=sqlite3.Row):
        self.connection = sqlite3.connect(databaseName)
        self.connection.row_factory = rowFactory
        # Must explicitly enable foreign keys for sqlite
        _ = self.executeAndCommitSQLStatement("PRAGMA foreign_keys=ON", columnNamesClassWrapper=None)

    def executeAndCommitSQLStatement[columnNamesGenericType: columnNames](self, SQLStatement: str, placeholderValues: tuple | dict = (), columnNamesClassWrapper: type[columnNamesGenericType] | None = columnNames, IsScript=False) -> tuple[list, columnNamesGenericType | None]:
        """
        Creates a cursor and then executes a sql statement with the provided placeholder values
        then commits and cleans up the cursor
        :param SQLStatement: A SQL statement to execute. If IsScript is True, then this is assumed to be a script.
        :param placeholderValues: Values for the placeholders in the statement. If IsScript is True, then this does nothing.
        :param columnNamesClassWrapper: If None, then no column names are provided in the returned tuple, otherwise a columnNames inherited class is used to store and decorate the column names from the query.
                                        If IsScript is True, returned column names may not be usable or just empty.
        :param IsScript: If true run SqlStatement as a script via executeScript otherwise execute SqlStatement as a regular query.
        :return: The result of the execute statement which may be the result set for a SELECT query or nothing useful for other queries like INSERT paired with the queries' column names along with a blank slate of web attributes
        """
        cursor = self.connection.cursor()
        # Non Select statements return an empty list, otherwise select statement will return the query results as a list
        result = cursor.execute(SQLStatement, placeholderValues).fetchall() if not IsScript else cursor.executescript(SQLStatement).fetchall()
        self.connection.commit()
        if columnNamesClassWrapper:
            columnNamesObj = columnNamesClassWrapper(columnNames.getColumnNamesListFromSqlCursorDescription(cursor.description))
            returnresult = (result, columnNamesObj)
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
    def lowercaseKeyDictSqlResultFactory(cursor, row):
        fields = [column[0] for column in cursor.description]
        return lowerCaseKeyDict({key: value for key, value in zip(fields, row)})