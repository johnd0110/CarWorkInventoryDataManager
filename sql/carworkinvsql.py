from collections.abc import Iterable
from typing import Protocol, Any
from flask import g

from .sql_infrastructure import baseSQL
from web.helper import columnNamesAndAttributes, VisibilityOptions

SCHEMA_FILE_PATH = "..\\sql\\schema\\schema.sql"
TEST_DATA_FILE_PATH = "..\\sql\\test_data\\manual_testing_data.sql"
DATABASE_FILE_PATH = "sql\\databases\\CWI_Database.db"

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

    def CWI_executeAndCommitSQLStatement(self, SQLStatement: str, placeholderValues: tuple | dict = (), returnColumnNames: bool = True) -> tuple[list, columnNamesAndAttributes | None]:
        """
        Custom call to executeAndCommitSQLStatement that provides the ColumnNamesAndAttributes class type
        so that the column names provided back have the extra configurable attributes for the HTML table display attached
        :param SQLStatement: SQL query statement to execute as a string
        :param placeholderValues: SQL Placeholder values as a tuple or dictionary
        :return: A tuple of the SQL query results and the column names with the configurable attributes as an columnNamesAndAttributes object
        """
        return self.executeAndCommitSQLStatement(SQLStatement, placeholderValues, columnNamesClassWrapper=columnNamesAndAttributes if returnColumnNames else None)

    @autoSetHiddenColumnsByNames(["carID"])
    def getCars(self) -> tuple[list, columnNamesAndAttributes | None]:
        return self.CWI_executeAndCommitSQLStatement("SELECT carID, make, model, year, engineType, mileage, initialCost FROM Cars")

    @autoSetHiddenColumnsByNames(["carID"])
    def getCarsWithViewEditLinksAndTotalValue(self) -> tuple[list, columnNamesAndAttributes | None]:
        return self.CWI_executeAndCommitSQLStatement("""SELECT c.carID, 
                                                               c.make, 
                                                               c.model, 
                                                               c.year, 
                                                               c.engineType, 
                                                               c.mileage, 
                                                               c.initialCost, 
                                                               (SELECT TOTAL(p.taxesPaid) + TOTAL(p.shippingCost) + TOTAL(p.price) FROM Parts p WHERE c.carID = p.InCarID) + (SELECT TOTAL(we.estimatedPay) FROM WorkEfforts we WHERE c.carID = we.carIDWorkedOn) + c.initialCost AS [totalEstimatedValue], 
                                                               'View' as viewLink, 
                                                               'Edit' as editLink 
                                                               FROM Cars c """)

    @autoSetHiddenColumnsByNames(["carID"])
    def getCarById(self, carID: int) -> tuple[list, columnNamesAndAttributes | None]:
        return self.CWI_executeAndCommitSQLStatement("""SELECT c.carID, 
                                                                            c.make, 
                                                                            c.model, 
                                                                            c.year, 
                                                                            c.engineType, 
                                                                            c.mileage, 
                                                                            c.initialCost, 
                                                                            (SELECT TOTAL(p.taxesPaid) + TOTAL(p.shippingCost) + TOTAL(p.price) FROM Parts p WHERE c.carID = p.InCarID) 
                                                                            + (SELECT TOTAL(we.estimatedPay) FROM WorkEfforts we WHERE c.carID = we.carIDWorkedOn) 
                                                                            + c.initialCost AS [totalEstimatedValue] 
                                                                            FROM Cars c 
                                                                            WHERE carID = ?""",
                                                     (carID,))

    @autoSetHiddenColumnsByNames(["partID", "InCarID"])
    def getParts(self) -> tuple[list, columnNamesAndAttributes | None]:
        return self.CWI_executeAndCommitSQLStatement("SELECT partID, InCarID, partName, taxesPaid, shippingCost, price FROM Parts")

    @autoSetHiddenColumnsByNames(["partID", "InCarID"])
    def getPartsForCar(self, carID: int) -> tuple[list, columnNamesAndAttributes | None]:
        return self.CWI_executeAndCommitSQLStatement("SELECT partID, InCarID, partName, taxesPaid, shippingCost, price FROM Parts WHERE InCarID = ?", placeholderValues=(carID,))

    @autoSetHiddenColumnsByNames(["employeeKey"])
    def getEmployees(self) -> tuple[list, columnNamesAndAttributes | None]:
        return self.CWI_executeAndCommitSQLStatement("SELECT employeeKey, employeeName FROM Employees")

    @autoSetHiddenColumnsByNames(["workEffortID", "carIDWorkedOn", "employeeWorkerKey"])
    def getWorkEfforts(self) -> tuple[list, columnNamesAndAttributes | None]:
        return self.CWI_executeAndCommitSQLStatement("SELECT workEffortID, carIDWorkedOn, employeeWorkerKey, workEffortDate, laborHours, estimatedPay, workType FROM WorkEfforts")

    @autoSetHiddenColumnsByNames(["workEffortID", "carIDWorkedOn", "employeeWorkerKey"])
    def getWorkEffortByCar(self, carID: int) -> tuple[list, columnNamesAndAttributes | None]:
        return self.CWI_executeAndCommitSQLStatement("""SELECT workEffortID, carIDWorkedOn, employeeWorkerKey, workEffortDate, laborHours, estimatedPay, workType 
                                                                     FROM WorkEfforts 
                                                                     WHERE CarIDWorkedOn = ?""", placeholderValues=(carID,))

    @autoSetHiddenColumnsByNames(["workEffortID", "carIDWorkedOn", "employeeWorkerKey"])
    def getWorkEffortByCarWithEmployees(self, carID: int) -> tuple[list, columnNamesAndAttributes | None]:
        return self.CWI_executeAndCommitSQLStatement("""SELECT we.workEffortID, we.carIDWorkedOn, we.employeeWorkerKey, 
                                                                     emp.EmployeeName, workEffortDate, laborHours, estimatedPay, workType 
                                                                     FROM WorkEfforts we 
                                                                     JOIN Employees emp 
                                                                     ON we.employeeWorkerKey = emp.employeeKey 
                                                                     WHERE we.CarIDWorkedOn = ?""",
                                                                  placeholderValues=(carID,))

    def insertCar(self, carDataValues: dict[str, Any]):
        return self.CWI_executeAndCommitSQLStatement("""INSERT INTO Cars(make, model, year, engineType, mileage, initialcost) 
                                                             VALUES (:make, :model, :year, :enginetype, :mileage, :initialcost)""",
                                                     carDataValues,
                                                     False)

    def insertEmployee(self, employeeDataValues: dict[str, Any]):
        return self.CWI_executeAndCommitSQLStatement("INSERT INTO Employees(employeeName) VALUES (:employeename)",
                                                     employeeDataValues,
                                                     False)

    def insertPart(self, partDataValues: dict[str, Any]):
        return self.CWI_executeAndCommitSQLStatement("INSERT INTO Parts(InCarID, partName, taxesPaid, shippingCost, price) VALUES (:incarid, :partname, :taxespaid, :shippingcost, :price)",
                                                     partDataValues,
                                                     False)

    def insertWorkEffort(self, workEffortDataValues: dict[str, Any]):
        return self.CWI_executeAndCommitSQLStatement("INSERT INTO WorkEfforts(carIDWorkedOn, employeeWorkerKey, workEffortDate, laborHours, estimatedPay, workType) VALUES (:caridworkedon, :employeeworkerkey, :workeffortdate, :laborhours, :estimatedpay, :worktype)",
                                                     workEffortDataValues,
                                                     False)

    @staticmethod
    def CWI_SQL_flask_factory():
        """
        Factory for connecting to a database within a Flask application for a car work inventory application.
        :return: The instance of the car work inventory SQL database manager that's been stored in g.db
        """
        if 'db' not in g:
            g.db = carWorkInventorySQL(databaseName=DATABASE_FILE_PATH, rowFactory=carWorkInventorySQL.lowercaseKeyDictSqlResultFactory)
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

    @staticmethod
    def CWI_SQL_flask_initialize_db(app, use_test_data=False):
        """
        Initialization function for a car work inventory SQL database as part of a Flask application.
        :param app: A Flask application
        :return: Nothing
        """
        with app.app_context():
            db = carWorkInventorySQL.CWI_SQL_flask_factory()
            with app.open_resource(SCHEMA_FILE_PATH) as f:
                db.executeAndCommitSQLStatement(f.read().decode('utf-8'), columnNamesClassWrapper=None, IsScript=True)

            if use_test_data:
                with app.open_resource(TEST_DATA_FILE_PATH) as f:
                    db.executeAndCommitSQLStatement(f.read().decode('utf-8'), columnNamesClassWrapper=None, IsScript=True)

            db.connection.commit()