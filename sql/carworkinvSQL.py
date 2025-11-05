import sqlite3
from argparse import ArgumentError

class baseSQL:
    def __init__(self):
        #TODO: Reassess the connection and look for a better way for handling the database connection in dev vs non-dev
        self.connection = sqlite3.connect(':memory:')

    def executeAndCommitSQLStatement(self, SQLStatement: str, placeholderValues: tuple = (), closeCursor = False):
        """
        Creates a cursor and then executes a sql statement with the provided placeholder values
        then commits and cleans up the cursor
        :param SQLStatement: A SQL statement to execute
        :param placeholderValues: Values for the placeholders in the statement
        :return: The result of the execute statement which is just the cursor itself or None if closeCursor is True
        """
        cursor = self.connection.cursor()
        result = cursor.execute(SQLStatement, placeholderValues)
        self.connection.commit()
        if closeCursor:
            cursor.close()
            return None
        else:
            return result

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

class testSQL(baseSQL):
    def __init__(self):
        super().__init__()
        self.executeAndCommitSQLStatement(f"CREATE TABLE test(testColumn)")

        self.executeAndCommitSQLStatement("INSERT INTO test (testColumn) VALUES (?)", ("This is a test",))

if __name__ == '__main__':
    test = testSQL()
    result = test.executeAndCommitSQLStatement("SELECT * FROM test")
    if result is not None:
        print(result.fetchall())
    else:
        print("No Result found.")


