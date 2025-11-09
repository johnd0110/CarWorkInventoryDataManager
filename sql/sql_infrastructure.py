import sqlite3
from argparse import ArgumentError

# Constant for switching to testing in a non-committal manner i.e. Testing SQL in memory rather than an actual database
NON_COMMITTAL_TEST = True

class baseSQL:
    def __init__(self, databaseName=":memory:", rowFactory=sqlite3.Row):
        self.connection = sqlite3.connect(databaseName)
        self.connection.row_factory = rowFactory
        # Must explicitly enable foreign keys for sqlite
        _ = self.executeAndCommitSQLStatement("PRAGMA foreign_keys=ON")

    def executeAndCommitSQLStatement(self, SQLStatement: str, placeholderValues: tuple = (), returnColumnNames = False, IsScript=False):
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
            returnresult = (result, [colTuple[0] for colTuple in cursor.description])
        else:
            returnresult = (result, [])
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


