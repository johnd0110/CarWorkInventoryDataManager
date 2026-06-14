import unittest
import sqlite3
import os
from unittest import TestCase
from tempfile import mkstemp
from pathlib import Path
from datetime import datetime
from time import sleep

from sql.carworkinvsql import CWIDatabaseFactory, SCHEMA_FILE_PATH
from common_helper import lowerCaseKeyDict

UNIT_TEST_DATA_PATH = "test_data/unittest_data.sql"

class DatabaseTests(TestCase):
    def setUp(self):
        self.tmpFileTuple = mkstemp()
        self.db = CWIDatabaseFactory(self.tmpFileTuple[1])

        # Program is too fast when generating timestamps in the unit test data
        # So we set up a custom sleep function to be called between the purchase updates
        # In order to have effective dates with different time stamps
        self.db.connection.create_function('sleep', 1, sleep)

        self.db.connection.set_authorizer(None)
        with open(Path(__file__).parent.parent.resolve() / 'sql' / SCHEMA_FILE_PATH, encoding='utf-8') as schemaFile:
            self.db.executeAndCommitSQLStatement(schemaFile.read(), columnNamesClassWrapper=None, IsScript=True)

        with open(Path(__file__).parent.parent.resolve() / 'sql' / UNIT_TEST_DATA_PATH, encoding='utf-8') as unitTestDataFile:
            self.db.executeAndCommitSQLStatement(unitTestDataFile.read(), columnNamesClassWrapper=None, IsScript=True)
        self.db.connection.set_authorizer(self.db.CWISqlAuthorizerCallback)

    def tearDown(self):
        self.db.cleanup()
        os.close(self.tmpFileTuple[0])

    def exceptionMessageTester(self, ex, exMsgToCheck, assertMsg, func, *funcArgs, **funcKwargs):
        with self.assertRaises(ex) as error:
            func(*funcArgs, **funcKwargs)
        exceptionmessage = str(error.exception)
        self.assertTrue(exceptionmessage.lower().startswith(exMsgToCheck.lower()),
                        msg=f"{assertMsg} {exceptionmessage}")

    def sqlIntegrityErrorMessageTester(self, exMsgToCheck, assertMsg, func, *funcArgs, **funcKwargs):
        self.exceptionMessageTester(sqlite3.IntegrityError, exMsgToCheck, assertMsg, func, *funcArgs, **funcKwargs)

    def authorizationTester(self, *funcArgs, **funcKwargs):
        self.exceptionMessageTester(sqlite3.DatabaseError,
                                    'not authorized',
                                    'Database error is not an authorization error. exception: ',
                                    self.db.CWI_executeAndCommitSQLStatement,
                                    *funcArgs,
                                    **funcKwargs)

    def testDatabaseSelect(self):
        self.assertGreater(len(self.db.CWI_executeAndCommitSQLStatement("SELECT * FROM CARS", returnColumnNames=False)[0]), 0)

        self.assertGreater(len(self.db.CWI_executeAndCommitSQLStatement("SELECT * FROM Items", returnColumnNames=False)[0]), 0)

        self.assertGreater(len(self.db.CWI_executeAndCommitSQLStatement("SELECT * FROM Employees", returnColumnNames=False)[0]), 0)

        self.assertGreater(len(self.db.CWI_executeAndCommitSQLStatement("SELECT * FROM WorkEfforts", returnColumnNames=False)[0]), 0)

        self.assertGreater(len(self.db.CWI_executeAndCommitSQLStatement("SELECT * FROM PurchasesHistory", returnColumnNames=False)[0]), 0)

        self.assertGreater(len(self.db.CWI_executeAndCommitSQLStatement("SELECT * FROM ItemGroupTransactions", returnColumnNames=False)[0]), 0)

        self.assertGreater(len(self.db.CWI_executeAndCommitSQLStatement("SELECT * FROM ValueEstimates", returnColumnNames=False)[0]), 0)

        self.assertGreater(len(self.db.CWI_executeAndCommitSQLStatement("SELECT * FROM Purchases", returnColumnNames=False)[0]), 0)

        # Test selecting from purchase history, make sure that versions and effective dates are in order.
        purchaseHistoryRes, _ = self.db.CWI_executeAndCommitSQLStatement('SELECT * FROM PurchasesHistory WHERE purchaseKey = 1 ORDER BY version', returnColumnNames=False)
        self.assertEqual(len(purchaseHistoryRes), 4)
        for i, purchaseHistoryRow in enumerate(purchaseHistoryRes):
            with self.subTest(version=i):
                self.assertEqual(purchaseHistoryRow['version'], i)

        dateFormatString = '%Y-%m-%d %H:%M:%S'
        self.assertTrue(all(datetime.strptime(dateBefore['effectiveDate'], dateFormatString) <= datetime.strptime(dateAfter['effectiveDate'], dateFormatString) for dateBefore, dateAfter in zip(purchaseHistoryRes, purchaseHistoryRes[1:])))

    def testDatabaseInsert(self):
        #Test valid inserts on all the tables, when insert succeeds, no results are provided and no error should occur

        # This also tests an insert on the Purchases and Value Estimates tables
        self.assertEqual(len(self.db.insertCar(lowerCaseKeyDict({'make': 'toyota', 'model': 'camry', 'year': 2010, 'enginetype': 'v9', 'mileage': 12345, 'cost': 12345, 'taxespaid': 1, 'shippingcost': 1, 'refundAmount': 0, 'estimatedvalue': 100, 'additionalnotes': ''}))[0]), 1)

        # Tests purchases and value estimate tables again but for items in addition to the items and item group transactions tables
        self.assertEqual(len(self.db.insertItem(lowerCaseKeyDict({'incarkey': 1, 'itemname': 'hub cap', 'taxespaid': 50.23, 'shippingcost': 12.34, 'cost': 123, 'refundamount': 0, 'estimatedvalue': 10, 'itemgroupdescription': 'test', 'source': '', 'additionalnotes': ''}))[0]), 1)

        self.assertEqual(len(self.db.insertEmployee(lowerCaseKeyDict({'employeename': 'jimbo'}))[0]), 1)

        self.assertEqual(len(self.db.insertWorkEffort(lowerCaseKeyDict({'carkeyworkedon': 1, 'employeekey': 1, 'workeffortdate': '2020-01-02', 'laborhours': 12, 'estimatedpay': 1234, 'worktype': 'engine replacement'}))[0]), 1)

        def insertWorkEffortDateCheckConstraintTest(date):
            self.sqlIntegrityErrorMessageTester('check constraint failed',
                                                'Database error is not a check constraint error.',
                                                self.db.insertWorkEffort,
                                                lowerCaseKeyDict({'carkeyworkedon': 1, 'employeekey': 1, 'workeffortdate': date, 'laborhours': 1, 'estimatedpay': 1, 'worktype': 'tire replacement'}))

        # Test Invalid Date: '2024-20-01' Expected result: Check constraint violation
        insertWorkEffortDateCheckConstraintTest('2024-20-01')

        # Test near leap year dates: '2023-02-30' Expected result: Check constraint violation
        insertWorkEffortDateCheckConstraintTest('2024-02-30')

        # Test improperly formated dates '2022-0-10', '2023-5-0' Expected Result: Check constraint violation
        insertWorkEffortDateCheckConstraintTest('2024-0-10')
        insertWorkEffortDateCheckConstraintTest('2024-5-0')

        # Test invalid foreign key inserts Expected result: Foreign key constraint violation
        def insertForeignKeyConstraintTest(insertFunc, *args):
            self.sqlIntegrityErrorMessageTester("foreign key constraint failed",
                                                'Database error is not a foreign key constraint error. exception: ',
                                                insertFunc,
                                                *args)

        # Test car key foreign key on items table
        insertForeignKeyConstraintTest(self.db.insertItem, lowerCaseKeyDict({'incarkey': 100000, 'itemname': 'hub cap', 'taxespaid': 50.23, 'shippingcost': 12.34, 'cost': 123, 'refundamount': 0, 'estimatedvalue': None, 'itemgroupdescription': '', 'source': '', 'additionalnotes': ''}))

        # Test item group transaction foreign key on items table
        insertForeignKeyConstraintTest(self.db.insertItem, lowerCaseKeyDict({'incarkey': 1, 'itemgrouptransactionkey': 100000, 'itemname': 'hub cap', 'taxespaid': 50.23, 'shippingcost': 12.34, 'cost': 123, 'refundamount': 0, 'estimatedvalue': None, 'itemgroupdescription': '', 'source': '', 'additionalnotes': ''}))

        # Test that item inserts prevent linking to a pre-existing purchase key
        self.assertRaises(ValueError,
                          self.db.insertItem,
                          lowerCaseKeyDict({'incarkey': 1, 'purchasekey': 100000, 'itemname': 'hub cap', 'taxespaid': 50.23, 'shippingcost': 12.34, 'cost': 123, 'refundamount': 0, 'estimatedvalue': None, 'itemgroupdescription': '', 'source': '', 'additionalnotes': ''}))

        # Test purchase foreign key on items table
        insertForeignKeyConstraintTest(self.db.CWI_executeAndCommitSQLStatement, "INSERT INTO Items(itemGroupTransactionKey, purchaseKey, itemName) VALUES(1, 1000000, '')")

        insertForeignKeyConstraintTest(self.db.insertWorkEffort, lowerCaseKeyDict({'carkeyworkedon': 999999, 'employeekey': 1, 'workeffortdate': '2019-08-12', 'laborhours': 1, 'estimatedpay': 1, 'worktype': 'tire replacement'}))
        insertForeignKeyConstraintTest(self.db.insertWorkEffort, lowerCaseKeyDict({'carkeyworkedon': 1, 'employeekey': 999999, 'workeffortdate': '2019-08-12', 'laborhours': 1, 'estimatedpay': 1, 'worktype': 'tire replacement'}))
        insertForeignKeyConstraintTest(self.db.insertWorkEffort, lowerCaseKeyDict({'carkeyworkedon': 888888, 'employeekey': 999999, 'workeffortdate': '2019-08-12', 'laborhours': 1, 'estimatedpay': 1, 'worktype': 'tire replacement'}))

        # Test purchase foreign key on cars table
        insertForeignKeyConstraintTest(self.db.CWI_executeAndCommitSQLStatement, 'INSERT INTO Cars(purchaseKey, make, model, year, engineType) VALUES (100000, \'\', \'\', \'\', \'\')')

        # Test that the authorizer callback on the database disallows inserts on purchase history table
        self.authorizationTester('INSERT INTO PurchasesHistory(purchaseKey, version, effectiveDate) VALUES (1000, 1000, \'12-31-9999\')', returnColumnNames=False)

    def testDatabaseUpdate(self):
        #Test valid updates on all columns (except primary keys and foreign keys) for each table, when update succeeds, no results are returned and no error should occur
        self.assertEqual(len(self.db.CWI_executeAndCommitSQLStatement("UPDATE Cars SET make='toyota', model='corolla', year=2022, engineType='V6', mileage=10000, additionalNotes='test' WHERE carKey=1", returnColumnNames=False)[0]), 0)
        # TODO: Test updating purchases or value estimates of specific car/item keys
        self.assertEqual(len(self.db.CWI_executeAndCommitSQLStatement("UPDATE Items SET inCarKey=2, itemName='car seat', source='amazon', additionalNotes='test' WHERE itemKey=1", returnColumnNames=False)[0]), 0)

        self.assertEqual(len(self.db.CWI_executeAndCommitSQLStatement("UPDATE Employees SET employeeName='jimbojimbo' WHERE employeekey=1", returnColumnNames=False)[0]), 0)

        self.assertEqual(len(self.db.CWI_executeAndCommitSQLStatement("UPDATE WorkEfforts SET workEffortDate='2022-11-24', laborHours=13, estimatedPay=140, workType='hub cap replacement' WHERE workEffortKey=1", returnColumnNames=False)[0]), 0)

        def updateCheckConstraintTest(date):
            self.sqlIntegrityErrorMessageTester('check constraint failed',
                                                'Database error is not a check constraint error. exception: ',
                                                self.db.CWI_executeAndCommitSQLStatement,
                                                "UPDATE WorkEfforts SET workEffortDate = ? WHERE workEffortKey=1", (date,),
                                                returnColumnNames=False)

        # Test Invalid Date: '2024-20-01' Expected result: Check constraint violation
        updateCheckConstraintTest('2024-20-01')

        # Test near leap year dates: '2023-02-30' Expected result: Check constraint violation
        updateCheckConstraintTest('2023-02-30')

        # Test improperly formated dates '2022-0-10', '2023-5-0' Expected Result: Check constraint violation
        updateCheckConstraintTest('2022-0-10')
        updateCheckConstraintTest('2023-5-0')

        def updateForeignKeyConstraintTest(SQLStatement):
            self.sqlIntegrityErrorMessageTester('foreign key constraint failed',
                                                'Database error is not a foreign key constraint error. exception: ',
                                                self.db.CWI_executeAndCommitSQLStatement,
                                                SQLStatement,
                                                returnColumnNames=False)

        # Test updates of parent keys that are set to ON UPDATE RESTRICT Expected Result: foreign key constraint violation
        updateForeignKeyConstraintTest("UPDATE Employees SET employeekey=100 WHERE employeekey=1")
        updateForeignKeyConstraintTest("UPDATE Purchases SET purchaseKey=100 WHERE purchaseKey=1")
        updateForeignKeyConstraintTest("UPDATE ItemGroupTransactions SET itemGroupTransactionKey=100 WHERE itemGroupTransactionKey=1")
        updateForeignKeyConstraintTest("UPDATE ValueEstimates SET valueEstimateKey=100 WHERE valueEstimateKey=1")

        # Test foreign key changes to a non-existent key Expected result: Foreign key constraint violation
        updateForeignKeyConstraintTest("UPDATE Items SET inCarKey=1000000 WHERE itemKey=1")

        # Item key = 2 should have valueEstimateKey = NULL, thus setting it to a key is allowed,
        # but not if it does not reference a real row
        updateForeignKeyConstraintTest("UPDATE Items SET valueEstimateKey=1000000 WHERE itemKey=2")

        # On Cars Table NULL -> New value estimate key is allowed, but not if the key does not reference an actual row
        updateForeignKeyConstraintTest("UPDATE Cars SET valueEstimateKey=100000 WHERE carKey=1")

        # Test that the validation update trigger on the Cars tables stops the update
        def carsTableValidationTriggerTest(SQLStatement):
            self.sqlIntegrityErrorMessageTester('Updates to the cars foreign keys are not allowed.',
                                                'Unknown error: ',
                                                self.db.CWI_executeAndCommitSQLStatement,
                                                SQLStatement,
                                                returnColumnNames=False)
        carsTableValidationTriggerTest("UPDATE Cars SET purchaseKey=100000 WHERE carKey=1")
        carsTableValidationTriggerTest("UPDATE Cars SET purchaseKey=100000 WHERE carKey=1")

        def itemsTableValidationTriggerTest(SQLStatement):
            self.sqlIntegrityErrorMessageTester('Updates to the items foreign keys are not allowed.',
                                                'Unknown error: ',
                                                self.db.CWI_executeAndCommitSQLStatement,
                                                SQLStatement,
                                                returnColumnNames=False)
        itemsTableValidationTriggerTest("UPDATE Items SET itemGroupTransactionKey=1000000 WHERE itemKey=1")
        itemsTableValidationTriggerTest("UPDATE Items SET purchaseKey=1000000 WHERE itemKey=1")
        # Item key = 1 in the unit test data already has a value estimate key set
        # Thus setting to another key is not allowed by the validation trigger
        itemsTableValidationTriggerTest("UPDATE Items SET valueEstimateKey=1000000 WHERE itemKey=1")

        def workEffortsTableValidationTriggerTest(SQLStatement):
            self.sqlIntegrityErrorMessageTester('Updates to the work efforts foreign keys are not allowed.',
                                                'Unknown error: ',
                                                self.db.CWI_executeAndCommitSQLStatement,
                                                SQLStatement,
                                                returnColumnNames=False)
        workEffortsTableValidationTriggerTest("UPDATE WorkEfforts SET carKeyWorkedOn=99999 WHERE workEffortKey=1")
        workEffortsTableValidationTriggerTest("UPDATE WorkEfforts SET employeeKey=88888 WHERE workEffortKey=1")
        workEffortsTableValidationTriggerTest("UPDATE WorkEfforts SET carKeyWorkedOn=99999, employeeKey=88888 WHERE workEffortKey=1")

        # Test that authorizer stops updates on the purchase history table
        self.authorizationTester("UPDATE PurchasesHistory SET purchaseKey=100000 WHERE purchaseKey=1", returnColumnNames=False)

        # If authorizer somehow allows the update on purchases history to go through,
        # test that the validation trigger on the table stops the update
        self.db.connection.set_authorizer(None)
        self.sqlIntegrityErrorMessageTester('Updates on PurchasesHistory are not allowed in order to maintain history integrity.',
                                            'Unknown error:',
                                            self.db.CWI_executeAndCommitSQLStatement,
                                            "UPDATE PurchasesHistory SET cost=100000 WHERE purchaseKey=1")
        self.db.connection.set_authorizer(self.db.CWISqlAuthorizerCallback)

    def testDatabaseDelete(self):
        #Test authorization stops deletes on all tables
        self.authorizationTester("DELETE FROM PurchasesHistory WHERE purchaseKey=1 AND version=0", returnColumnNames=False)
        self.authorizationTester("DELETE FROM WorkEfforts WHERE workEffortKey=1", returnColumnNames=False)
        self.authorizationTester("DELETE FROM Items WHERE itemKey=1", returnColumnNames=False)
        self.authorizationTester("DELETE FROM ItemGroupTransactions WHERE itemGroupTransactionKey=1", returnColumnNames=False)
        self.authorizationTester("DELETE FROM Cars WHERE carKey=1", returnColumnNames=False)
        self.authorizationTester("DELETE FROM Employees WHERE employeeKey=1", returnColumnNames=False)
        self.authorizationTester("DELETE FROM ValueEstimates WHERE valueEstimateKey=1", returnColumnNames=False)
        self.authorizationTester("DELETE FROM Purchases WHERE purchaseKey=1", returnColumnNames=False)

        # Test authorizer stops delete of all rows in tables
        # Deletion order matters due to the foreign key constraints
        self.authorizationTester("DELETE FROM WorkEfforts WHERE workEffortKey=1", returnColumnNames=False)
        self.authorizationTester("DELETE FROM Items WHERE itemKey=1", returnColumnNames=False)
        self.authorizationTester("DELETE FROM ItemGroupTransactions WHERE itemGroupTransactionKey=1", returnColumnNames=False)
        self.authorizationTester("DELETE FROM Cars WHERE carKey=1", returnColumnNames=False)
        self.authorizationTester("DELETE FROM Employees WHERE employeeKey=1", returnColumnNames=False)
        self.authorizationTester("DELETE FROM ValueEstimates WHERE valueEstimateKey=1", returnColumnNames=False)
        self.authorizationTester("DELETE FROM Purchases WHERE purchaseKey=1", returnColumnNames=False)

    def testDatabasePrimaryKeys(self):
        def testUniqueConstraint(SQLStatement):
            self.sqlIntegrityErrorMessageTester('unique constraint failed',
                                                'Database error is not a unique constraint error. exception: ',
                                                self.db.CWI_executeAndCommitSQLStatement,
                                                SQLStatement,
                                                returnColumnNames=False)

        #Test unique primary keys are enforced
        testUniqueConstraint("UPDATE Cars SET carKey=3 WHERE carKey=2")
        testUniqueConstraint("UPDATE Items SET itemKey=3 WHERE itemKey=2")
        testUniqueConstraint("UPDATE Employees SET employeekey=3 WHERE employeekey=2")
        testUniqueConstraint("UPDATE WorkEfforts SET workEffortKey=3 WHERE workEffortKey=2")
        testUniqueConstraint("UPDATE ItemGroupTransactions SET itemGroupTransactionKey=3 WHERE itemGroupTransactionKey=2")
        testUniqueConstraint("UPDATE Purchases SET purchaseKey=3 WHERE purchaseKey=2")
        testUniqueConstraint("UPDATE ValueEstimates SET valueEstimateKey=3 WHERE valueEstimateKey=2")
        # Purchases History Updates are not allowed

if __name__ == '__main__':
    unittest.main()