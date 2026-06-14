from collections.abc import Iterable
from typing import Protocol
from flask import g
import sqlite3

from common_helper import lowerCaseKeyDict
from sql.sql_infrastructure import baseSQL
from web.helper import columnNamesAndAttributes, VisibilityOptions
from config.default_config import DATABASE_URI

SCHEMA_FILE_PATH = "schema/schema.sql"

class queryCaller(Protocol):
    def __call__(self, param: int) -> tuple[list, columnNamesAndAttributes]:
        ...

def autoSetHiddenColumnsByNames(columnNames: Iterable[str]):
    def autoSetHiddenColumnsByNames(func: queryCaller):
        def wrapper(*args, **kwargs):
            results, columnNamesAndAttrs = func(*args, **kwargs)
            for columnName in columnNames:
                columnNamesAndAttrs[columnName].visibility = VisibilityOptions.COLLAPSE.value
            return results, columnNamesAndAttrs
        return wrapper
    return autoSetHiddenColumnsByNames

class carWorkInventorySQL(baseSQL):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.connection.set_authorizer(carWorkInventorySQL.CWISqlAuthorizerCallback)

    def CWI_executeAndCommitSQLStatement(self, SQLStatement: str, placeholderValues: tuple | dict = (), returnColumnNames: bool = True, keepTransactionOpen: bool = False) -> tuple[list, columnNamesAndAttributes | None]:
        """
        Custom call to executeAndCommitSQLStatement that provides the ColumnNamesAndAttributes class type
        so that the column names provided back have the extra configurable attributes for the HTML table display attached
        :param keepTransactionOpen:
        :param returnColumnNames:
        :param SQLStatement: SQL query statement to execute as a string
        :param placeholderValues: SQL Placeholder values as a tuple or dictionary
        :return: A tuple of the SQL query results and the column names with the configurable attributes as an columnNamesAndAttributes object
        """
        return self.executeAndCommitSQLStatement(SQLStatement,
                                                 placeholderValues,
                                                 columnNamesClassWrapper=columnNamesAndAttributes if returnColumnNames else None,
                                                 keepTransactionOpen=keepTransactionOpen)

    @autoSetHiddenColumnsByNames(["carKey"])
    def getCarsWithViewEditLinksAndTotalValue(self) -> tuple[list, columnNamesAndAttributes | None]:
        return self.CWI_executeAndCommitSQLStatement("""SELECT c.carKey, 
                                                               c.make, 
                                                               c.model, 
                                                               c.year, 
                                                               c.engineType, 
                                                               c.mileage, 
                                                               p.taxesPaid,
                                                               p.shippingCost,
                                                               p.cost,
                                                               p.refundAmount,
                                                               p.totalSpent as purchaseTotal,
                                                                
                                                               (SELECT TOTAL(p.totalSpent)
                                                                FROM Items itm
                                                                JOIN purchases p
                                                                ON itm.purchaseKey = p.purchaseKey 
                                                                WHERE c.carKey = itm.inCarKey) + 
                                                               (SELECT TOTAL(we.estimatedPay) 
                                                                FROM WorkEfforts we 
                                                                WHERE c.carKey = we.carKeyWorkedOn) + 
                                                               p.totalSpent AS [totalInvestedValue],
                                                                
                                                               COALESCE(ve.estimatedValue, 0) as estimatedValue, 
                                                               c.additionalNotes,
                                                               'View' as viewLink,
                                                               'Edit' as editLink 
                                                               FROM Cars c
                                                               JOIN Purchases p
                                                               ON c.purchaseKey = p.purchaseKey
                                                               LEFT JOIN ValueEstimates ve
                                                               ON c.valueEstimateKey = ve.valueEstimateKey""")

    @autoSetHiddenColumnsByNames(["carKey"])
    def getCarById(self, carID: int) -> tuple[list, columnNamesAndAttributes | None]:
        return self.CWI_executeAndCommitSQLStatement("""SELECT c.carKey, 
                                                                            c.make, 
                                                                            c.model, 
                                                                            c.year, 
                                                                            c.engineType, 
                                                                            c.mileage,
                                                                            p.taxesPaid,
                                                                            p.shippingCost,
                                                                            p.cost,
                                                                            p.refundAmount,
                                                                            p.totalSpent as purchaseTotal,
                                                                             
                                                                            (SELECT TOTAL(p.totalSpent)
                                                                             FROM Items itm
                                                                             JOIN purchases p
                                                                             ON itm.purchaseKey = p.purchaseKey 
                                                                             WHERE c.carKey = itm.inCarKey) + 
                                                                            (SELECT TOTAL(we.estimatedPay) 
                                                                             FROM WorkEfforts we 
                                                                             WHERE c.carKey = we.carKeyWorkedOn) + 
                                                                            p.totalSpent AS [totalInvestedValue], 
                                                                            
                                                                            COALESCE(ve.estimatedValue, 0) as estimatedValue,
                                                                            c.additionalNotes
                                                                            FROM Cars c
                                                                            JOIN Purchases p
                                                                            ON c.purchaseKey = p.purchaseKey
                                                                            LEFT JOIN ValueEstimates ve
                                                                            ON c.valueEstimateKey = ve.valueEstimateKey
                                                                            WHERE c.carKey = ?""",
                                                     (carID,))

    @autoSetHiddenColumnsByNames(["itemKey", "inCarKey"])
    def getItemsForCar(self, carID: int) -> tuple[list, columnNamesAndAttributes | None]:
        return self.CWI_executeAndCommitSQLStatement("""SELECT itm.itemKey, 
                                                                           itm.inCarKey, 
                                                                           itm.itemName, 
                                                                           p.taxesPaid, 
                                                                           p.shippingCost, 
                                                                           p.cost,
                                                                           p.refundAmount,
                                                                           p.totalSpent as purchaseTotal,
                                                                           COALESCE(ve.estimatedValue, 'N/A') as estimatedValue, 
                                                                           itm.additionalNotes 
                                                                           FROM Items itm
                                                                           JOIN Purchases p
                                                                           ON itm.purchaseKey = p.purchaseKey
                                                                           LEFT JOIN ValueEstimates ve
                                                                           ON itm.valueEstimateKey = ve.valueEstimateKey 
                                                                           WHERE itm.inCarKey = ?""", placeholderValues=(carID,))

    @autoSetHiddenColumnsByNames(["employeeKey"])
    def getEmployees(self) -> tuple[list, columnNamesAndAttributes | None]:
        return self.CWI_executeAndCommitSQLStatement("SELECT employeeKey, employeeName FROM Employees")

    @autoSetHiddenColumnsByNames(["workEffortKey", "carKeyWorkedOn", "employeeKey"])
    def getWorkEffortByCarWithEmployees(self, carID: int) -> tuple[list, columnNamesAndAttributes | None]:
        return self.CWI_executeAndCommitSQLStatement("""SELECT we.workEffortKey, 
                                                                           we.carKeyWorkedOn, 
                                                                           we.employeeKey, 
                                                                           emp.EmployeeName, 
                                                                           we.workEffortDate, 
                                                                           we.laborHours, 
                                                                           we.estimatedPay, 
                                                                           we.workType 
                                                                     FROM WorkEfforts we 
                                                                     JOIN Employees emp 
                                                                     ON we.employeeKey = emp.employeeKey 
                                                                     WHERE we.carKeyWorkedOn = ?""",
                                                                  placeholderValues=(carID,))

    def _insertPurchaseWithOpenTransaction(self, purchaseDataValues: lowerCaseKeyDict):
        """
        Insert a purchase row with an open transaction so that it may be paired with another query.
        :param purchaseDataValues: Purchase data values as a dictionary of column names: values
        :return: A sql result set with the newly inserted purchase key
        """
        purchaseKeyResult, _ = self.CWI_executeAndCommitSQLStatement("""INSERT INTO Purchases(cost, taxesPaid, shippingCost, refundAmount)
                                                                                    VALUES (:cost, :taxespaid, :shippingcost, :refundamount)
                                                                                    RETURNING purchaseKey""",
                                                                     purchaseDataValues.data,
                                                                     False,
                                                                     keepTransactionOpen=True)
        purchaseKeyColumnName = "purchaseKey"
        purchaseDataValues[purchaseKeyColumnName] = purchaseKeyResult[0][purchaseKeyColumnName]

    def _insertValueEstimateWithOpenTransaction(self, valueEstimateDataValues: lowerCaseKeyDict):
        """
        Insert a value estimate row with an open transaction so that it may be paired with another query.
        :param valueEstimateDataValues: Value Estimate data values as a dictionary of column names: values
        :return: Nothing, the data values argument gets updated with the returned key
        """
        valueEstimateKeyColumnName = "valueEstimateKey"
        if valueEstimateDataValues['estimatedValue']:

            valueEstimateKeyResult, _ = self.CWI_executeAndCommitSQLStatement("""INSERT INTO ValueEstimates(estimatedValue)
                                                            VALUES (:estimatedvalue)
                                                            RETURNING valueEstimateKey
                                                            """,
                                                         valueEstimateDataValues.data,
                                                         False,
                                                         keepTransactionOpen=True)
            valueEstimateDataValues[valueEstimateKeyColumnName] = valueEstimateKeyResult[0][valueEstimateKeyColumnName]
        else:
            valueEstimateDataValues[valueEstimateKeyColumnName] = None

    def _insertItemGroupTransactionWithOpenTransaction(self, itemGroupTransactionDataValues: lowerCaseKeyDict):
        itemGroupTransactionKeyResult, _ = self.CWI_executeAndCommitSQLStatement("""INSERT INTO ItemGroupTransactions(description)
                                                                                                VALUES (:itemgroupdescription)
                                                                                                RETURNING itemGroupTransactionKey""",
                                                                                 itemGroupTransactionDataValues.data,
                                                                                 False,
                                                                                 keepTransactionOpen=True)
        itemGroupTransactionKeyColumnName = "itemGroupTransactionKey"
        itemGroupTransactionDataValues[itemGroupTransactionKeyColumnName] = itemGroupTransactionKeyResult[0][itemGroupTransactionKeyColumnName]

    def insertCar(self, carDataValues: lowerCaseKeyDict):
        """
        Inserts a car row with purchase data.

        A purchase row is inserted first to get a purchase key to then assign to the car row we insert.

        Everything is done in the same transaction and when the car row is inserted, the transaction is committed.
        :param carDataValues: Car data with purchase data
        :return: Result of the insert, which is nothing (No RETURNING Clause)
        """
        self._insertPurchaseWithOpenTransaction(carDataValues)
        self._insertValueEstimateWithOpenTransaction(carDataValues)
        return self.CWI_executeAndCommitSQLStatement("""INSERT INTO Cars(purchaseKey, valueEstimateKey, make, model, year, engineType, mileage, additionalNotes) 
                                                                    VALUES (:purchasekey, :valueestimatekey, :make, :model, :year, :enginetype, :mileage, :additionalnotes)
                                                                    RETURNING carKey""",
                                                     carDataValues.data,
                                                     False)

    def insertEmployee(self, employeeDataValues: lowerCaseKeyDict):
        return self.CWI_executeAndCommitSQLStatement("""INSERT INTO Employees(employeeName) 
                                                                    VALUES (:employeename)
                                                                    RETURNING employeeKey""",
                                                     employeeDataValues.data,
                                                     False)

    def insertItem(self, itemDataValues: lowerCaseKeyDict):
        if itemDataValues.get('purchaseKey') is not None:
            raise ValueError(f'Cannot insert item linked to an existing purchase key.')

        self._insertPurchaseWithOpenTransaction(itemDataValues)

        if itemDataValues.get('valueEstimateKey') is not None:
            raise ValueError(f'Cannot insert item linked to an existing value estimate key.')

        self._insertValueEstimateWithOpenTransaction(itemDataValues)

        # If no item group transaction key provided, then create a new one for the item,
        # otherwise just add the item with the provided item group transaction key so the link is created
        #TODO: Consider reworking to only create an item group transaction only when more than one items are grouped
        # instead of a item group transaction for one or more items always
        if itemDataValues.get('itemGroupTransactionKey') is None:
            self._insertItemGroupTransactionWithOpenTransaction(itemDataValues)

        return self.CWI_executeAndCommitSQLStatement("""INSERT INTO Items(itemGroupTransactionKey, purchaseKey, valueEstimateKey, inCarKey, itemName, source, additionalNotes) 
                                                                    VALUES (:itemgrouptransactionkey, :purchasekey, :valueestimatekey, :incarkey, :itemname, :source, :additionalnotes)
                                                                    RETURNING itemKey""",
                                                     itemDataValues.data,
                                                     False)

    def insertWorkEffort(self, workEffortDataValues: lowerCaseKeyDict):
        return self.CWI_executeAndCommitSQLStatement("""INSERT INTO WorkEfforts(carKeyWorkedOn, employeeKey, workEffortDate, laborHours, estimatedPay, workType) 
                                                                    VALUES (:carkeyworkedon, :employeekey, :workeffortdate, :laborhours, :estimatedpay, :worktype)
                                                                    RETURNING workEffortKey""",
                                                     workEffortDataValues.data,
                                                     False)

    def updateCarPurchaseAndValueEstimate(self, carDataValues: lowerCaseKeyDict):
        parentKeysToUpdateResult, _ = self.CWI_executeAndCommitSQLStatement("""SELECT c.purchaseKey,
                                                                               c.valueEstimateKey
                                                                               FROM Cars c
                                                                               WHERE c.carKey = :carkey""",
                                                                            carDataValues.data,
                                                                            False)


        valueEstimateKeyColumnName = "valueEstimateKey"
        if parentKeysToUpdateResult[0][valueEstimateKeyColumnName]:
            #TODO: If no estimated value set then delete value estimate row and set car value estimate key to null
            carDataValues[valueEstimateKeyColumnName] = parentKeysToUpdateResult[0][valueEstimateKeyColumnName]
            _ = self.CWI_executeAndCommitSQLStatement("""UPDATE ValueEstimates
                                                         SET estimatedValue = :estimatedvalue
                                                         WHERE valueEstimateKey = :valueestimatekey""",
                                                      carDataValues.data,
                                                      False,
                                                      True)
        else:
            self._insertValueEstimateWithOpenTransaction(carDataValues)

        purchaseKeyColumnName = "purchaseKey"
        carDataValues[purchaseKeyColumnName] = parentKeysToUpdateResult[0][purchaseKeyColumnName]

        _ = self.CWI_executeAndCommitSQLStatement("""UPDATE Purchases
                                                     SET cost = :cost,
                                                     taxesPaid = :taxespaid,
                                                     shippingCost = :shippingcost,
                                                     refundAmount = :refundamount
                                                     WHERE purchaseKey = :purchasekey""",
                                                  carDataValues.data,
                                                  False)

        _ = self.CWI_executeAndCommitSQLStatement("""UPDATE Cars 
                                                               SET make = :make, 
                                                               model = :model, 
                                                               year = :year, 
                                                               engineType = :enginetype, 
                                                               mileage = :mileage,
                                                               additionalNotes = :additionalnotes,
                                                               valueEstimateKey = :valueestimatekey
                                                               WHERE carKey = :carkey""",
                                                               carDataValues.data,
                                                               False)

    def nonParentExistsForParentTable(self, unsafeParentTableName: str, unsafeParentKeyColumnName: str) -> bool:
        """
        Determines if the given parent table name has any primary keys that do not have any child rows
        Assumes that the parent table only has
        :param unsafeParentKeyColumnName:
        :param unsafeParentTableName:
        :return:
        """
        # TODO: To be tested
        # Ensure that the parent table name and parent key column name is a valid table and column name in the database schema
        table_name_res, _ = self.executeAndCommitSQLStatement("""SELECT sch.tbl_name as table_name,
                                                                 tbl_info.name as column_name
                                                                 FROM sqlite_schema sch, 
                                                                 pragma_table_xinfo(sch.tbl_name) tbl_info
                                                                 WHERE sch.type = 'table'
                                                                 AND sch.tbl_name = ?
                                                                 AND tbl_info.name = ?""",
                                                              (unsafeParentTableName, unsafeParentKeyColumnName),
                                                              columnNamesClassWrapper=None)
        if len(table_name_res) <= 0:
            raise ValueError(f"Parent table does not exist: {unsafeParentTableName}.")
        elif len(table_name_res) > 1:
            raise ValueError(f"More than one {unsafeParentTableName} table exists. This should not be possible.")

        # Use the table name and column name from the query since we know those should be safe
        # instead of the arguments
        safeParentTableName = table_name_res[0].pop('table_name')
        safeParentKeyColumnName = table_name_res[0].pop('column_name')

        table_column_res, _ = self.executeAndCommitSQLStatement(f"""SELECT *
                                                                   FROM pragma_table_xinfo()""")

        # Get all child table names for parentTableName and the associated child key column
        child_tables_res, _ = self.executeAndCommitSQLStatement("""SELECT sch.tbl_name as child_table_name, 
                                                                          fkl.from as child_key_column 
                                                                   FROM sqlite_schema sch,
                                                                   pragma_foreign_key_list(sch.tbl_name) fkl
                                                                   WHERE sch.type = 'table'
                                                                   AND fkl.table = ?
                                                                   AND fkl.to = ?""",
                                                                (safeParentTableName, safeParentKeyColumnName),
                                                                columnNamesClassWrapper=None)

        # Dynamically build out a query to see if the parent table has any non-parent rows
        nonParentPurchaseSelectQuery = f"SELECT * FROM {safeParentTableName} parent WHERE NOT ("
        for index, child_table_row in enumerate(child_tables_res):
            child_table_name, child_key_column_name = child_table_row.items()
            nonParentPurchaseSelectQuery += f"EXISTS(SELECT 1 FROM {child_table_name} WHERE {child_key_column_name} = parent.{safeParentKeyColumnName}"
            if index != len(child_tables_res) - 1:
                nonParentPurchaseSelectQuery += " OR"
        nonParentPurchaseSelectQuery += ")"

        nonParentRowsResult, _ = self.executeAndCommitSQLStatement(nonParentPurchaseSelectQuery,
                                                                   columnNamesClassWrapper=None)

        # If the query returned any rows
        # then there exists a row in the given parent table that does not have a child row
        return len(nonParentRowsResult) > 0

    @staticmethod
    def CWISqlAuthorizerCallback(actionCode: int, actionParam1 : str | None, actionParam2: str | None, databaseName: str | None, responsibleTriggerOrViewName: str | None) -> int | None:
        """
        Car Work Inventory Database Sqlite3 authorizer callback function

        In most cases it uses the base class authorizer

        :param actionCode: Sqlite Action code i.e. SQLITE_SELECT
        :param actionParam1: Action parameter for the provided action code (could be None) refer to sqlite documentation for authorizers
        :param actionParam2: Action parameter for the provided action code (could be None) refer to sqlite documentation for authorizers
        :param databaseName: Database name the action is being performed from
        :param responsibleTriggerOrViewName: The trigger or view responsible for the action (if any)
        :return: SQLITE_DENY, SQLITE_OK, or SQLITE_IGNORE code
        """
        # Disallow any inserts to the purchases history table except through the trigger that manages generating the history rows
        if (actionCode == sqlite3.SQLITE_INSERT
                and actionParam1.lower() == 'purchaseshistory'
                and responsibleTriggerOrViewName.lower() != 'generatehistoryrowandverifypurchaseupdate'):
            return sqlite3.SQLITE_DENY
        elif actionCode == sqlite3.SQLITE_UPDATE and actionParam1.lower() == 'purchaseshistory':
            return sqlite3.SQLITE_DENY

        # Otherwise use the base authorizer
        return carWorkInventorySQL.baseSQLAuthorizerCallback(actionCode, actionParam1, actionParam2, databaseName, responsibleTriggerOrViewName)

    @staticmethod
    def CWI_SQL_flask_factory():
        """
        Factory for connecting to a database within a Flask application for a car work inventory application.
        :return: The instance of the car work inventory SQL database manager that's been stored in g.db
        """
        if 'db' not in g:
            g.db = CWIDatabaseFactory()
        return g.db

    @staticmethod
    def CWI_SQL_flask_teardown(exception):
        """
        Flask Teardown context handler for cleaning up the database connection/instance if it exists in a Flask application context
        :param exception: Exception provided by the Flask application teardown context
        :return: Nothing
        """
        db = g.pop('db', None)

        if db is not None:
            db.cleanup()

def CWIDatabaseFactory(filePath = DATABASE_URI) -> carWorkInventorySQL:
    return carWorkInventorySQL(databaseName=filePath, rowFactory=carWorkInventorySQL.lowercaseKeyDictSqlResultFactory)