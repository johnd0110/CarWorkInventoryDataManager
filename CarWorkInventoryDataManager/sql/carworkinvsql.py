from collections.abc import Iterable
from typing import Protocol
import sqlite3

from ..common_helper import lowerCaseKeyDict
from .sql_infrastructure import baseSQL
from datastructures import columnNamesAndAttributes, VisibilityOptions

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

    def CWI_executeSQLStatement(self, SQLStatement: str, placeholderValues: tuple | dict = (), returnColumnNames: bool = True, keepTransactionOpen: bool = False) -> tuple[list, columnNamesAndAttributes | None]:
        """
        Custom call to executeAndCommitSQLStatement that provides the ColumnNamesAndAttributes class type
        so that the column names provided back have the extra configurable attributes for the HTML table display attached
        :param keepTransactionOpen: Boolean to determine if the statement execution results should be committed on completion or leave the transaction open
        :param returnColumnNames: Boolean for if column names should be returned in the second tuple element, otherwise it is None
        :param SQLStatement: SQL query statement to execute as a string
        :param placeholderValues: SQL Placeholder values as a tuple or dictionary
        :return: A tuple of the SQL query results and the column names with the configurable attributes as an columnNamesAndAttributes object
        """
        return self.executeSQLStatement(SQLStatement,
                                        placeholderValues,
                                        columnNamesClassWrapper=columnNamesAndAttributes if returnColumnNames else None,
                                        keepTransactionOpen=keepTransactionOpen)

    @autoSetHiddenColumnsByNames(["carKey", "purchaseKey"])
    def getCarsWithViewEditLinksAndTotalValue(self) -> tuple[list, columnNamesAndAttributes | None]:
        return self.CWI_executeSQLStatement("""SELECT c.carKey, 
                                                      c.make, 
                                                      c.model, 
                                                      c.year, 
                                                      c.engineType, 
                                                      c.mileage,
                                                      p.purchaseKey,
                                                      p.taxesPaid,
                                                      p.shippingCost,
                                                      p.cost,
                                                      p.refundAmount,
                                                      p.purchaseTotal,
                                                                
                                                      (SELECT TOTAL(p.purchaseTotal)
                                                       FROM Items itm
                                                       JOIN purchases p
                                                       ON itm.purchaseKey = p.purchaseKey
                                                       JOIN ItemsToCars itc
                                                       ON c.carKey = itc.carKey
                                                       AND itm.itemKey = itc.itemKey) + 
                                                       (SELECT TOTAL(we.estimatedPay) 
                                                        FROM WorkEfforts we 
                                                        WHERE c.carKey = we.carKeyWorkedOn) + 
                                                      p.purchaseTotal AS [totalInvestedValue],
                                                      CASE 
                                                        WHEN ve.estimatedValue = 0 THEN NULL 
                                                        ELSE ve.estimatedValue 
                                                      END as estimatedValue, 
                                                      c.additionalNotes,
                                                      'View' as viewLink,
                                                      'Edit' as editLink,
                                                      'View/Edit Purchase Data' as viewEditPurchaseDataLink
                                                      FROM Cars c
                                                      JOIN Purchases p
                                                      ON c.purchaseKey = p.purchaseKey
                                                      LEFT JOIN ValueEstimates ve
                                                      ON c.valueEstimateKey = ve.valueEstimateKey""")

    @autoSetHiddenColumnsByNames(["carKey", "purchaseKey"])
    def getCarByKey(self, carKey: int) -> tuple[list, columnNamesAndAttributes | None]:
        return self.CWI_executeSQLStatement("""SELECT c.carKey, 
                                                                   c.make, 
                                                                   c.model, 
                                                                   c.year, 
                                                                   c.engineType, 
                                                                   c.mileage,
                                                                   p.purchaseKey,
                                                                   p.taxesPaid,
                                                                   p.shippingCost,
                                                                   p.cost,
                                                                   p.refundAmount,
                                                                   p.purchaseTotal,
                                                                    
                                                                   (SELECT TOTAL(p.purchaseTotal)
                                                                    FROM Items itm
                                                                    JOIN purchases p
                                                                    ON itm.purchaseKey = p.purchaseKey
                                                                    JOIN ItemsToCars itc 
                                                                    ON c.carKey = itc.carKey
                                                                    AND itm.itemKey = itc.itemKey) + 
                                                                   (SELECT TOTAL(we.estimatedPay) 
                                                                    FROM WorkEfforts we 
                                                                    WHERE c.carKey = we.carKeyWorkedOn) + 
                                                                   p.purchaseTotal AS [totalInvestedValue], 
                                                                   CASE 
                                                                     WHEN ve.estimatedValue = 0 THEN NULL 
                                                                     ELSE ve.estimatedValue 
                                                                   END as estimatedValue, 
                                                                   c.additionalNotes,
                                                                   'View/Edit Purchase Data' as viewEditPurchaseDataLink
                                                                   FROM Cars c
                                                                   JOIN Purchases p
                                                                   ON c.purchaseKey = p.purchaseKey
                                                                   LEFT JOIN ValueEstimates ve
                                                                   ON c.valueEstimateKey = ve.valueEstimateKey
                                                                   WHERE c.carKey = ?""",
                                            (carKey,))

    @autoSetHiddenColumnsByNames(["itemGroupTransactionKey", "itemKey", "carKey", "purchaseKey"])
    def getItemsAndItemGroupTransactionsForCar(self, carKey) -> tuple[list, columnNamesAndAttributes | None]:
        return self.CWI_executeSQLStatement("""SELECT itg.itemGroupTransactionKey,
                                                                  itg.description as itemGroupDescription,
                                                                  itm.itemKey,
                                                                  itc.carKey,
                                                                  itm.source,
                                                                  itm.itemName,
                                                                  p.purchaseKey,
                                                                  p.taxesPaid,
                                                                  p.shippingCost,
                                                                  p.cost,
                                                                  p.refundAmount,
                                                                  p.purchaseTotal,
                                                                  CASE 
                                                                    WHEN ve.estimatedValue = 0 THEN NULL 
                                                                    ELSE ve.estimatedValue 
                                                                  END as estimatedValue, 
                                                                  itm.additionalNotes,
                                                                  itm.isGeneralPurpose,
                                                                  'View/Edit Purchase Data' as viewEditPurchaseDataLink
                                                                  FROM itemGroupTransactions itg
                                                                  JOIN Items itm 
                                                                  ON itg.itemGroupTransactionKey = itm.itemGroupTransactionKey
                                                                  JOIN ItemsToCars itc
                                                                  ON ? = itc.carKey
                                                                  AND itm.itemKey = itc.itemKey
                                                                  JOIN Purchases p
                                                                  ON itm.purchaseKey = p.purchaseKey
                                                                  LEFT JOIN ValueEstimates ve
                                                                  ON itm.valueEstimateKey = ve.valueEstimateKey""",
                                            (carKey,))

    @autoSetHiddenColumnsByNames(["itemKey", "carKey", "purchaseKey"])
    def getItemsForCar(self, carKey: int) -> tuple[list, columnNamesAndAttributes | None]:
        return self.CWI_executeSQLStatement("""SELECT itm.itemKey, 
                                                                  itc.carKey,
                                                                  itm.source, 
                                                                  itm.itemName,
                                                                  p.purchaseKey, 
                                                                  p.taxesPaid, 
                                                                  p.shippingCost, 
                                                                  p.cost,
                                                                  p.refundAmount,
                                                                  p.purchaseTotal,
                                                                  CASE 
                                                                    WHEN ve.estimatedValue = 0 THEN NULL 
                                                                    ELSE ve.estimatedValue 
                                                                  END as estimatedValue, 
                                                                  itm.additionalNotes,
                                                                  itm.isGeneralPurpose,
                                                                  'View/Edit Purchase Data' as viewEditPurchaseDataLink 
                                                                  FROM Items itm
                                                                  JOIN ItemsToCars itc
                                                                  ON ? = itc.carKey
                                                                  AND itm.itemKey = itc.itemKey
                                                                  JOIN Purchases p
                                                                  ON itm.purchaseKey = p.purchaseKey
                                                                  LEFT JOIN ValueEstimates ve
                                                                  ON itm.valueEstimateKey = ve.valueEstimateKey""",
                                            placeholderValues=(carKey,))

    @autoSetHiddenColumnsByNames(["itemKey", "carKey", "purchaseKey"])
    def getGeneralPurposeItemsAndLinkedCars(self) -> tuple[list, columnNamesAndAttributes | None]:
        return self.CWI_executeSQLStatement("""SELECT itm.itemKey,
                                                      itm.source,
                                                      itm.itemName,
                                                      p.purchaseKey,
                                                      p.taxesPaid,
                                                      p.shippingCost,
                                                      p.cost,
                                                      p.refundAmount,
                                                      p.purchaseTotal,
                                                      CASE 
                                                        WHEN ve.estimatedValue = 0 THEN NULL 
                                                        ELSE ve.estimatedValue 
                                                      END as estimatedValue, 
                                                      itm.additionalNotes,
                                                      'View/Edit Purchase Data' as viewEditPurchaseDataLink,
                                                      c.carKey,
                                                      c.make,
                                                      c.model,
                                                      c.year,
                                                      c.engineType
                                               FROM Items itm
                                               JOIN ItemsToCars itc
                                               ON itm.itemKey = itc.itemKey
                                               JOIN Purchases p
                                               ON itm.purchaseKey = p.purchaseKey
                                               JOIN Cars c
                                               ON itc.carKey = c.carKey
                                               WHERE itm.isGeneralPurpose = TRUE""")
    
    @autoSetHiddenColumnsByNames(["employeeKey"])
    def getEmployees(self) -> tuple[list, columnNamesAndAttributes | None]:
        return self.CWI_executeSQLStatement("SELECT employeeKey, employeeName FROM Employees")

    @autoSetHiddenColumnsByNames(["workEffortKey", "carKeyWorkedOn", "employeeKey"])
    def getWorkEffortByCarWithEmployees(self, carKey: int) -> tuple[list, columnNamesAndAttributes | None]:
        return self.CWI_executeSQLStatement("""SELECT we.workEffortKey, 
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
                                            placeholderValues=(carKey,))

    @autoSetHiddenColumnsByNames(["version"])
    def getPurchaseHistoryAndCurrentPurchaseDataByKey(self, purchaseKey: int) -> tuple[list, columnNamesAndAttributes | None]:
        return self.CWI_executeSQLStatement("""SELECT ph.effectiveDate as changedDate,
                                                                  ph.version,
                                                                  ph.cost,
                                                                  ph.taxesPaid,
                                                                  ph.shippingCost,
                                                                  ph.refundAmount
                                                           FROM PurchasesHistory ph
                                                           WHERE ph.purchaseKey = :purchasekey
                                                           UNION ALL
                                                           SELECT "CURRENT" as changedDate,
                                                                  (SELECT MAX(ph.version) + 1 FROM PurchasesHistory ph WHERE ph.purchaseKey = p.purchaseKey) AS version,
                                                                  p.cost,
                                                                  p.taxesPaid,
                                                                  p.shippingCost,
                                                                  p.refundAmount
                                                           FROM Purchases p
                                                           WHERE p.purchaseKey = :purchasekey
                                                           ORDER BY version ASC
                                                           """,
                                                placeholderValues=lowerCaseKeyDict({"purchaseKey": purchaseKey}).data)

    def _insertPurchaseWithOpenTransaction(self, purchaseDataValues: lowerCaseKeyDict):
        """
        Insert a purchase row with an open transaction so that it may be paired with another query.
        :param purchaseDataValues: Purchase data values as a dictionary of column names: values
        :return: A sql result set with the newly inserted purchase key
        """
        purchaseKeyResult, _ = self.CWI_executeSQLStatement("""INSERT INTO Purchases(cost, taxesPaid, shippingCost, refundAmount)
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
        estimatedValueColumnName = 'estimatedValue'
        valueEstimateDataValues[estimatedValueColumnName] = valueEstimateDataValues.get(estimatedValueColumnName, 0)
        valueEstimateKeyResult, _ = self.CWI_executeSQLStatement("""INSERT INTO ValueEstimates(estimatedValue)
                                                                                VALUES (:estimatedvalue)
                                                                                RETURNING valueEstimateKey
                                                                                """,
                                                                 valueEstimateDataValues.data,
                                                                 False,
                                                                 keepTransactionOpen=True)
        valueEstimateKeyColumnName = "valueEstimateKey"
        valueEstimateDataValues[valueEstimateKeyColumnName] = valueEstimateKeyResult[0][valueEstimateKeyColumnName]

    def _insertItemGroupTransactionWithOpenTransaction(self, itemGroupTransactionDataValues: lowerCaseKeyDict):
        itemGroupTransactionKeyResult, _ = self.CWI_executeSQLStatement("""INSERT INTO ItemGroupTransactions(description)
                                                                                       VALUES (:itemgroupdescription)
                                                                                       RETURNING itemGroupTransactionKey""",
                                                                        itemGroupTransactionDataValues.data,
                                                                        False,
                                                                        keepTransactionOpen=True)
        itemGroupTransactionKeyColumnName = "itemGroupTransactionKey"
        itemGroupTransactionDataValues[itemGroupTransactionKeyColumnName] = itemGroupTransactionKeyResult[0][itemGroupTransactionKeyColumnName]

    def _insertItemToCarLinkWithOpenTransaction(self, itemToCarLinkDataValues: lowerCaseKeyDict):
        itemToCarKeyResult, _ = self.CWI_executeSQLStatement("""INSERT INTO ItemsToCars(itemKey, carKey)
                                                                VALUES (:itemkey, :carkey)""",
                                                             itemToCarLinkDataValues.data,
                                                             False,
                                                             keepTransactionOpen=True)

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
        return self.CWI_executeSQLStatement("""INSERT INTO Cars(purchaseKey, valueEstimateKey, make, model, year, engineType, mileage, additionalNotes) 
                                                           VALUES (:purchasekey, :valueestimatekey, :make, :model, :year, :enginetype, :mileage, :additionalnotes)
                                                           RETURNING carKey""",
                                            carDataValues.data,
                                            False)

    def insertEmployee(self, employeeDataValues: lowerCaseKeyDict):
        return self.CWI_executeSQLStatement("""INSERT INTO Employees(employeeName) 
                                                           VALUES (:employeename)
                                                           RETURNING employeeKey""",
                                            employeeDataValues.data,
                                            False)

    def insertSingleItem(self, itemDataValues: lowerCaseKeyDict, defaultNotGeneralPurpose = True, keepTransactionOpen: bool = False):
        if defaultNotGeneralPurpose:
            if itemDataValues.get('isGeneralPurpose', None) is not None:
                raise ValueError("Unexpected Error: General Purpose value exists, expected no general purpose to be set.")
            itemDataValues['isGeneralPurpose'] = False

        if itemDataValues.get('purchaseKey') is not None:
            raise ValueError(f'Cannot insert item linked to an existing purchase key.')

        self._insertPurchaseWithOpenTransaction(itemDataValues)

        if itemDataValues.get('valueEstimateKey') is not None:
            raise ValueError(f'Cannot insert item linked to an existing value estimate key.')

        self._insertValueEstimateWithOpenTransaction(itemDataValues)

        # If no item group transaction key provided, then create a new one for the item,
        # otherwise just add the item with the provided item group transaction key so the link is created
        if itemDataValues.get('itemGroupTransactionKey') is None:
            self._insertItemGroupTransactionWithOpenTransaction(itemDataValues)

        itemKeyResult = self.CWI_executeSQLStatement("""INSERT INTO Items(itemGroupTransactionKey, purchaseKey, valueEstimateKey, itemName, source, additionalNotes, isGeneralPurpose) 
                                                                       VALUES (:itemgrouptransactionkey, :purchasekey, :valueestimatekey, :itemname, :source, :additionalnotes, :isgeneralpurpose)
                                                                       RETURNING itemKey""",
                                                        itemDataValues.data,
                                                        False,
                                                        keepTransactionOpen)

        if itemDataValues.get('carKey') is not None:
            itemDataValues["itemKey"] = itemKeyResult[0][0]["itemKey"]
            self._insertItemToCarLinkWithOpenTransaction(itemDataValues)

        return itemKeyResult

    def insertMultipleItems(self, multiItemDataValues: list[lowerCaseKeyDict], canHaveGeneralPurpose: bool = False):
        itemGroupTransactionKey = None
        for index, itemDataValues in enumerate(multiItemDataValues):
            if itemGroupTransactionKey is not None:
                itemDataValues["itemgrouptransactionkey"] = itemGroupTransactionKey
            else:
                # Made it to other items without creating an item group transaction
                # This is not allowed in this method, we should be creating an item group transaction on the first item
                # so that subsequent items are added to the same item group transaction
                if index != 0:
                    raise ValueError("Failed to insert item group: First item should have an item group description element.")

            # Keep transaction open until the last item
            # When the last item is inserted, we commit the whole transaction to the database.
            self.insertSingleItem(itemDataValues, not canHaveGeneralPurpose, index < len(multiItemDataValues) - 1)

            if index == 0:
                itemGroupTransactionKey = itemDataValues["itemgrouptransactionkey"]

    def insertWorkEffort(self, workEffortDataValues: lowerCaseKeyDict):
        return self.CWI_executeSQLStatement("""INSERT INTO WorkEfforts(carKeyWorkedOn, employeeKey, workEffortDate, laborHours, estimatedPay, workType) 
                                                           VALUES (:carkeyworkedon, :employeekey, :workeffortdate, :laborhours, :estimatedpay, :worktype)
                                                           RETURNING workEffortKey""",
                                            workEffortDataValues.data,
                                            False)

    def updatePurchaseData(self, purchaseDataValues: lowerCaseKeyDict):
        return self.CWI_executeSQLStatement("""UPDATE Purchases
                                                           SET cost = :cost,
                                                           taxesPaid = :taxespaid,
                                                           shippingCost = :shippingcost,
                                                           refundAmount = :refundamount
                                                           WHERE purchaseKey = :purchasekey""",
                                             purchaseDataValues.data,
                                             False)

    def updateCarAndValueEstimate(self, carDataValues: lowerCaseKeyDict):
        parentKeysToUpdateResult, _ = self.CWI_executeSQLStatement("""SELECT c.valueEstimateKey
                                                                                         FROM Cars c
                                                                                         WHERE c.carKey = :carkey""",
                                                                   carDataValues.data,
                                                                   False)


        valueEstimateKeyColumnName = "valueEstimateKey"
        if parentKeysToUpdateResult[0][valueEstimateKeyColumnName]:
            if carDataValues["estimatedvalue"] is not None:
                carDataValues[valueEstimateKeyColumnName] = parentKeysToUpdateResult[0][valueEstimateKeyColumnName]
                _ = self.CWI_executeSQLStatement("""UPDATE ValueEstimates
                                                                SET estimatedValue = :estimatedvalue
                                                                WHERE valueEstimateKey = :valueestimatekey""",
                                                 carDataValues.data,
                                                 False,
                                                 True)
            # else no new estimated value provided, so no update needed
        else:
            self._insertValueEstimateWithOpenTransaction(carDataValues)

        _ = self.CWI_executeSQLStatement("""UPDATE Cars 
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

def CWIDatabaseFactory(filePath: str) -> carWorkInventorySQL:
    return carWorkInventorySQL(databaseName=filePath, rowFactory=carWorkInventorySQL.lowercaseKeyDictSqlResultFactory)