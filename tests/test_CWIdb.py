import unittest
from unittest import TestCase
from tempfile import mkstemp
import os
import sqlite3

from sql import carWorkInventorySQL
from sql.carworkinvsql import SCHEMA_FILE_PATH
from common_helper import lowerCaseKeyDict

UNIT_TEST_DATA_PATH = "..\\sql\\test_data\\unittest_data.sql"

def CWIDatabaseFactory(filePath):
    return carWorkInventorySQL(databaseName=filePath, rowFactory=carWorkInventorySQL.lowercaseKeyDictSqlResultFactory)

class DatabaseTests(TestCase):
    def setUp(self):
        self.tmpFileTuple = mkstemp()
        self.db = CWIDatabaseFactory(self.tmpFileTuple[1])
        with open(SCHEMA_FILE_PATH) as schemaFile:
            self.db.executeAndCommitSQLStatement(schemaFile.read(), columnNamesClassWrapper=None, IsScript=True)
            self.db.connection.commit()

        with open(UNIT_TEST_DATA_PATH) as unitTestDataFile:
            self.db.executeAndCommitSQLStatement(unitTestDataFile.read(), columnNamesClassWrapper=None, IsScript=True)
            self.db.connection.commit()

    def tearDown(self):
        self.db.cleanup()
        os.close(self.tmpFileTuple[0])

    def testDatabaseSelect(self):
        # Test select from cars table
        self.assertGreater(len(self.db.executeAndCommitSQLStatement("SELECT * FROM CARS", columnNamesClassWrapper=None)[0]), 0)

        # Parts table
        self.assertGreater(len(self.db.executeAndCommitSQLStatement("SELECT * FROM Parts", columnNamesClassWrapper=None)[0]), 0)

        # Employees table
        self.assertGreater(len(self.db.executeAndCommitSQLStatement("SELECT * FROM Employees", columnNamesClassWrapper=None)[0]), 0)

        # Work Effort Table
        self.assertGreater(len(self.db.executeAndCommitSQLStatement("SELECT * FROM WorkEfforts", columnNamesClassWrapper=None)[0]), 0)

    def testDatabaseInsert(self):

        #Test valid inserts on all the tables, when insert succeeds, no results are provided and no error should occur
        self.assertEqual(len(self.db.insertCar(lowerCaseKeyDict({'make': 'toyota', 'model': 'camry', 'year': 2010, 'enginetype': 'v9', 'mileage': 12345, 'initialcost': 12345}).lowercaseKeyDict)[0]), 0)
        self.assertEqual(len(self.db.insertPart(lowerCaseKeyDict({'incarid': 1, 'partname': 'hub cap', 'taxespaid': 50.23, 'shippingcost': 12.34, 'price': 123}).lowercaseKeyDict)[0]), 0)
        self.assertEqual(len(self.db.insertEmployee(lowerCaseKeyDict({'employeename': 'jimbo'}).lowercaseKeyDict)[0]), 0)
        self.assertEqual(len(self.db.insertWorkEffort(lowerCaseKeyDict({'caridworkedon': 1, 'employeeworkerkey': 1, 'workeffortdate': '2020-01-02', 'laborhours': 12, 'estimatedpay': 1234, 'worktype': 'engine replacement'}).lowercaseKeyDict)[0]), 0)

        def insertWorkEffortDateCheckConstraintTest(date):
            with self.assertRaises(sqlite3.IntegrityError) as checkconstrainterror:
                self.db.insertWorkEffort(lowerCaseKeyDict({'caridworkedon': 1, 'employeeworkerkey': 1, 'workeffortdate': date, 'laborhours': 1, 'estimatedpay': 1, 'worktype': 'tire replacement'}).lowercaseKeyDict)
            exceptionmessage = str(checkconstrainterror.exception)
            self.assertTrue(exceptionmessage.lower().startswith('check constraint failed'),
                            msg=f"Database error is not a check constraint error. {exceptionmessage}")

        # Test Invalid Date: '2024-20-01' Expected result: Check constraint violation
        insertWorkEffortDateCheckConstraintTest('2024-20-01')

        # Test near leap year dates: '2023-02-30' Expected result: Check constraint violation
        insertWorkEffortDateCheckConstraintTest('2024-02-30')

        # Test improperly formated dates '1', '2022-0-10', '2023-5-0' Expected Result: Check constraint violation
        insertWorkEffortDateCheckConstraintTest('2024-0-10')
        insertWorkEffortDateCheckConstraintTest('2024-5-0')

        # Test invalid foreign key inserts Expected result: Foreign key constraint violation
        def insertForeignKeyConstraintTest(insertFunc, data):
            with self.assertRaises(sqlite3.IntegrityError) as foreignkeyconstrainterror:
                insertFunc(data)
            exceptionmessage = str(foreignkeyconstrainterror.exception)
            self.assertTrue(exceptionmessage.lower().startswith("foreign key constraint failed"),
                            msg=f"Database error is not a foreign key constraint error. exception:{exceptionmessage}")

        insertForeignKeyConstraintTest(self.db.insertPart, lowerCaseKeyDict({'incarid': 100000, 'partname': 'hub cap', 'taxespaid': 50.23, 'shippingcost': 12.34, 'price': 123}).lowercaseKeyDict)
        insertForeignKeyConstraintTest(self.db.insertWorkEffort, lowerCaseKeyDict({'caridworkedon': 999999, 'employeeworkerkey': 1, 'workeffortdate': '2019-08-12', 'laborhours': 1, 'estimatedpay': 1, 'worktype': 'tire replacement'}).lowercaseKeyDict)
        insertForeignKeyConstraintTest(self.db.insertWorkEffort, lowerCaseKeyDict({'caridworkedon': 1, 'employeeworkerkey': 999999, 'workeffortdate': '2019-08-12', 'laborhours': 1, 'estimatedpay': 1, 'worktype': 'tire replacement'}).lowercaseKeyDict)
        insertForeignKeyConstraintTest(self.db.insertWorkEffort, lowerCaseKeyDict({'caridworkedon': 888888, 'employeeworkerkey': 999999, 'workeffortdate': '2019-08-12', 'laborhours': 1, 'estimatedpay': 1, 'worktype': 'tire replacement'}).lowercaseKeyDict)

    def testDatabaseUpdate(self):

        #Test valid updates on all columns (except primary keys) for each table, when update succeeds, no results are returned and no error should occur
        self.assertEqual(len(self.db.CWI_executeAndCommitSQLStatement("UPDATE Cars SET make='toyota', model='corolla', year='2022', engineType='V6', mileage=10000, initialCost=10000 WHERE carID=1", returnColumnNames=False)[0]), 0)
        self.assertEqual(len(self.db.CWI_executeAndCommitSQLStatement("UPDATE Parts SET InCarID=2, partName='car seat', taxesPaid=12, shippingcost=23, price=100 WHERE partID=1", returnColumnNames=False)[0]), 0)
        self.assertEqual(len(self.db.CWI_executeAndCommitSQLStatement("UPDATE Employees SET employeeName='jimbojimbo' WHERE employeekey=1", returnColumnNames=False)[0]), 0)
        self.assertEqual(len(self.db.CWI_executeAndCommitSQLStatement("UPDATE WorkEfforts SET carIDWorkedOn=2, employeeWorkerKey=2, workEffortDate='2022-11-24', laborHours=13, estimatedPay=140, workType='hub cap replacement' WHERE workEffortID=1", returnColumnNames=False)[0]), 0)

        #Test updates of parent keys that are set to ON UPDATE RESTRICT Expected Result:


        def updateCheckConstraintTest(date):
            with self.assertRaises(sqlite3.IntegrityError) as checkconstrainterror:
                self.db.CWI_executeAndCommitSQLStatement("UPDATE WorkEfforts SET workEffortDate = ? WHERE workEffortID=1", (date,))
            exceptionmessage = str(checkconstrainterror.exception)
            self.assertTrue(str(checkconstrainterror.exception).lower().startswith('check constraint failed'),
                            msg=f"Database error is not a check constraint error. exception: {exceptionmessage}")

        # Test Invalid Date: '2024-20-01' Expected result: Check constraint violation
        updateCheckConstraintTest('2024-20-01')

        # Test near leap year dates: '2023-02-30' Expected result: Check constraint violation
        updateCheckConstraintTest('2023-02-30')

        # Test improperly formated dates '2022-0-10', '2023-5-0' Expected Result: Check constraint violation
        updateCheckConstraintTest('2022-0-10')
        updateCheckConstraintTest('2023-5-0')

        def updateForeignKeyConstraintTest(SQLStatement):
            with self.assertRaises(sqlite3.IntegrityError) as foreignkeyconstrainterror:
                self.db.CWI_executeAndCommitSQLStatement(SQLStatement, returnColumnNames=False)
            exceptionmessage = str(foreignkeyconstrainterror.exception)
            self.assertTrue(str(foreignkeyconstrainterror.exception).lower().startswith('foreign key constraint failed'),
                            msg=f"Database error is not a foreign key constraint error. exception: {exceptionmessage}")

        # Test updates of parent keys that are set to ON UPDATE RESTRICT Expected Result: foreign key constraint violation
        updateForeignKeyConstraintTest("UPDATE Cars SET carID=100, make='toyota', model='corolla', year='2022', engineType='V6', mileage=10000, initialCost=10000 WHERE carID=1")
        updateForeignKeyConstraintTest("UPDATE Employees SET employeekey=100 WHERE employeekey=1")

        # Test foreign key changes to a non-existent key Expected result: Foreign key constraint violation
        updateForeignKeyConstraintTest("UPDATE Parts SET InCarID=1000000, partName='head rest', taxesPaid=66, shippingcost=88, price=56 WHERE partID=1")
        updateForeignKeyConstraintTest("UPDATE WorkEfforts SET carIDWorkedOn=99999, employeeWorkerKey=1, workEffortDate='2023-09-11', laborHours=08, estimatedPay=40, workType='body work' WHERE workEffortID=1")
        updateForeignKeyConstraintTest("UPDATE WorkEfforts SET carIDWorkedOn=1, employeeWorkerKey=88888, workEffortDate='2023-09-11', laborHours=08, estimatedPay=40, workType='body work' WHERE workEffortID=1")
        updateForeignKeyConstraintTest("UPDATE WorkEfforts SET carIDWorkedOn=99999, employeeWorkerKey=88888, workEffortDate='2023-09-11', laborHours=08, estimatedPay=40, workType='body work' WHERE workEffortID=1")

    def testDatabaseDelete(self):

        #Test valid delete of one row
        self.assertEqual(len(self.db.CWI_executeAndCommitSQLStatement("DELETE FROM Cars WHERE carID=4", returnColumnNames=False)[0]), 0)
        self.assertEqual(len(self.db.CWI_executeAndCommitSQLStatement("DELETE FROM Parts WHERE partID=1", returnColumnNames=False)[0]), 0)
        self.assertEqual(len(self.db.CWI_executeAndCommitSQLStatement("DELETE FROM Employees WHERE employeekey=4", returnColumnNames=False)[0]), 0)
        self.assertEqual(len(self.db.CWI_executeAndCommitSQLStatement("DELETE FROM WorkEfforts WHERE workEffortID=1", returnColumnNames=False)[0]), 0)

        def deleteParentKeyRestrictionConstraintTest(SQLStatement):
            with self.assertRaises(sqlite3.IntegrityError) as parentkeyrestrictionconstrainterror:
                self.db.CWI_executeAndCommitSQLStatement(SQLStatement, returnColumnNames=False)
            exceptionmessage = str(parentkeyrestrictionconstrainterror.exception)
            self.assertTrue(str(parentkeyrestrictionconstrainterror.exception).lower().startswith('foreign key constraint failed'),
                            msg=f"Database error is not a foreign key constraint error. exception: {exceptionmessage}")

        #Test deletion of parent keys that are set to ON DELETE RESTRICT Expected result:
        deleteParentKeyRestrictionConstraintTest("DELETE FROM Cars WHERE carID=1")
        deleteParentKeyRestrictionConstraintTest("DELETE FROM Employees WHERE employeeKey=1")

        #Test valid delete of all rows in tables
        # Deletion order matters due to the foreign key constraints
        self.assertEqual(len(self.db.CWI_executeAndCommitSQLStatement("DELETE FROM Parts", returnColumnNames=False)[0]), 0)
        self.assertEqual(len(self.db.CWI_executeAndCommitSQLStatement("DELETE FROM WorkEfforts", returnColumnNames=False)[0]), 0)
        self.assertEqual(len(self.db.CWI_executeAndCommitSQLStatement("DELETE FROM Cars", returnColumnNames=False)[0]), 0)
        self.assertEqual(len(self.db.CWI_executeAndCommitSQLStatement("DELETE FROM Employees", returnColumnNames=False)[0]), 0)

    def testDatabasePrimaryKeys(self):
        def testUniqueConstraint(SQLStatement):
            with self.assertRaises(sqlite3.IntegrityError) as uniqueconstrainterror:
                self.db.CWI_executeAndCommitSQLStatement(SQLStatement, returnColumnNames=False)
            exceptionmessage = str(uniqueconstrainterror.exception)
            self.assertTrue(str(uniqueconstrainterror.exception).lower().startswith('unique constraint failed'),
                            msg=f"Database error is not a unique constraint error. exception: {exceptionmessage}")

        #Test unique primary keys are enforced
        testUniqueConstraint("UPDATE Cars SET carID=3 WHERE carID=2")
        testUniqueConstraint("UPDATE Parts SET partID=3 WHERE partID=2")
        testUniqueConstraint("UPDATE Employees SET employeekey=3 WHERE employeekey=2")
        testUniqueConstraint("UPDATE WorkEfforts SET workEffortID=3 WHERE workEffortID=2")

if __name__ == '__main__':
    unittest.main()