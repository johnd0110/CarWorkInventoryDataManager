import sqlite3

from common_helper import lowerCaseKeyDict

class columnNames:
    """
    General class for storing SQL column names
    Can be inherited from to provide a standard way to store and access SQL column names
    and is the expected class type for storing column names coming out of SQL queries from baseSQL classses
    """
    def __init__(self, sqlColumnNames: list[str]):
        """
        :param sqlColumnNames: list of column names to assign to self.columnNames
        """

        # Strip down the cursor description tuple down to just the column names in a list
        self.columnNames = sqlColumnNames

    @staticmethod
    def getColumnNamesListFromSqlCursorDescription(sqlresultcolumnnames: tuple[tuple[str, None, None, None, None, None, None]]) -> list[str]:
        return [colTuple[0] for colTuple in sqlresultcolumnnames]

class baseSQL:
    """Base Class for providing common SQL functionality"""
    def __init__(self, databaseName=":memory:", rowFactory=sqlite3.Row):
        self.connection = sqlite3.connect(databaseName, autocommit=False)
        self.connection.row_factory = rowFactory
        # Must explicitly enable foreign keys for sqlite
        self.connection.setconfig(sqlite3.SQLITE_DBCONFIG_ENABLE_FKEY, True)

        # =============== Security measures ========================
        # Enable Sqlite's defensive measures for more safety
        self.connection.setconfig(sqlite3.SQLITE_DBCONFIG_DEFENSIVE, True)

        integrity_check_result, _ = self.executeAndCommitSQLStatement("PRAGMA integrity_check")

        self.connection.set_authorizer(baseSQL.baseSQLAuthorizerCallback)

    def executeAndCommitSQLStatement[columnNamesGenericType: columnNames](self, SQLStatement: str, placeholderValues: tuple | dict = (), columnNamesClassWrapper: type[columnNamesGenericType] | None = columnNames, IsScript=False, keepTransactionOpen: bool = False) -> tuple[list, columnNamesGenericType | None]:
        """
        Creates a cursor and then executes a sql statement with the provided placeholder values
        then commits and cleans up the cursor
        :param keepTransactionOpen: Boolean to determine whether to keep the transaction open after the statement executes.
        :param SQLStatement: A SQL statement to execute. If IsScript is True, then this is assumed to be a script.
        :param placeholderValues: Values for the placeholders in the statement. If IsScript is True, then this does nothing.
        :param columnNamesClassWrapper: If None, then no column names are provided in the returned tuple, otherwise a columnNames inherited class is used to store and decorate the column names from the query.
                                        If IsScript is True, returned column names may not be usable or just empty.
        :param IsScript: If true run SqlStatement as a script via executeScript otherwise execute SqlStatement as a regular query.
        :return: The result of the execute statement which may be the result set for a SELECT query or
                 nothing useful for other queries like INSERT paired with the queries' column names along with a blank slate of decorated (if at all) column names
                 UNLESS a returning clause is provided, in which case the results will be that of the returning clause
        """
        cursor = self.connection.cursor()
        # Non-Select statements return an empty list, otherwise select statement will return the query results as a list
        result = cursor.execute(SQLStatement, placeholderValues).fetchall() if not IsScript else cursor.executescript(SQLStatement).fetchall()

        if not keepTransactionOpen:
            self.connection.commit()

        if columnNamesClassWrapper:
            columnNamesObj = columnNamesClassWrapper(columnNames.getColumnNamesListFromSqlCursorDescription(cursor.description))
            returnresult = (result, columnNamesObj)
        else:
            returnresult = (result, None)
        cursor.close()
        return returnresult

    def cleanup(self):
        self.connection.close()

    @staticmethod
    def lowercaseKeyDictSqlResultFactory(cursor, row):
        fields = [column[0] for column in cursor.description]
        return lowerCaseKeyDict({key: value for key, value in zip(fields, row)})

    @staticmethod
    def baseSQLAuthorizerCallback(actionCode: int, actionParam1 : str | None, actionParam2: str | None, databaseName: str | None, responsibleTriggerOrViewName: str | None) -> int | None:
        """
        Generic/Default Sqlite3 authorizer callback function
        By default, only allows standard SQL actions to happen within the application such as SELECTS, INSERTS, UPDATES.

        :param actionCode: Sqlite Action code i.e. SQLITE_SELECT
        :param actionParam1: Action parameter for the provided action code (could be None) refer to sqlite documentation for authorizers
        :param actionParam2: Action parameter for the provided action code (could be None) refer to sqlite documentation for authorizers
        :param databaseName: Database name the action is being performed from
        :param responsibleTriggerOrViewName: The trigger or view responsible for the action (if any)
        :return: SQLITE_DENY, SQLITE_OK, or SQLITE_IGNORE code
        """
        match actionCode:
            # Create actions
            case sqlite3.SQLITE_CREATE_INDEX | sqlite3.SQLITE_CREATE_TABLE | sqlite3.SQLITE_CREATE_TEMP_INDEX | sqlite3.SQLITE_CREATE_TEMP_TABLE | sqlite3.SQLITE_CREATE_TEMP_TRIGGER | sqlite3.SQLITE_CREATE_TEMP_VIEW | sqlite3.SQLITE_CREATE_TRIGGER | sqlite3.SQLITE_CREATE_VIEW | sqlite3.SQLITE_CREATE_VTABLE:
                return sqlite3.SQLITE_DENY
            # Drop actions
            case sqlite3.SQLITE_DROP_INDEX | sqlite3.SQLITE_DROP_TABLE | sqlite3.SQLITE_DROP_TEMP_INDEX | sqlite3.SQLITE_DROP_TEMP_TABLE | sqlite3.SQLITE_DROP_TEMP_TRIGGER | sqlite3.SQLITE_DROP_TEMP_VIEW | sqlite3.SQLITE_DROP_TRIGGER | sqlite3.SQLITE_DROP_VIEW | sqlite3.SQLITE_DROP_VTABLE:
                return sqlite3.SQLITE_DENY
            case sqlite3.SQLITE_ALTER_TABLE:
                return sqlite3.SQLITE_DENY
            # Miscellaneous actions
            case sqlite3.SQLITE_PRAGMA | sqlite3.SQLITE_ATTACH | sqlite3.SQLITE_DETACH | sqlite3.SQLITE_REINDEX | sqlite3.SQLITE_ANALYZE | sqlite3.SQLITE_SAVEPOINT | sqlite3.SQLITE_RECURSIVE:
                return sqlite3.SQLITE_DENY
            case sqlite3.SQLITE_DELETE:
                # Prevent deletes in general as it is better to keep mistakes and correct using an update
                # So that auditing can be done
                return sqlite3.SQLITE_DENY
            case _:
                return sqlite3.SQLITE_OK