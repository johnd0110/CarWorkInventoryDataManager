from collections.abc import Iterable
from typing import Protocol
from sql.sql_infrastructure import baseSQL, columnNamesAndAttributes
from flask import g

SCHEMA_FILE_PATH = "..\\sql\\schema\\schema.sql"
TEST_DATA_FILE_PATH = "..\\sql\\test\\test_data.sql"
DATABASE_FILE_PATH = "sql\\databases\\CWI_Database.db"

class queryCaller(Protocol):
    def __call__(self, param: int) -> tuple[list, columnNamesAndAttributes]:
        ...

def autoSetHiddenColumnsByNames(columnNames: Iterable[str]):
    def autoSetHiddenColumnsByNames(func: queryCaller):
        def wrapper(*args, **kwargs):
            results, columnNamesAndAttrs = func(*args, **kwargs)
            for columnName in columnNames:
                columnNamesAndAttrs[columnName].visibility = "collapse"
            return results, columnNamesAndAttrs
        return wrapper
    return autoSetHiddenColumnsByNames

class carWorkInventorySQL(baseSQL):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @autoSetHiddenColumnsByNames(["carID"])
    def getCars(self) -> tuple[list, columnNamesAndAttributes]:
        return self.executeAndCommitSQLStatement("SELECT carID, make, model, year, engineType, mileage, initialCost FROM Cars", returnColumnNames=True)

    @autoSetHiddenColumnsByNames(["carID"])
    def getCarById(self, carID: int) -> tuple[list, columnNamesAndAttributes]:
        return self.executeAndCommitSQLStatement("SELECT carID, make, model, year, engineType, mileage, initialCost FROM Cars WHERE carID = ?", (carID,), returnColumnNames=True)

    @autoSetHiddenColumnsByNames(["partID", "InCarID"])
    def getParts(self) -> tuple[list, columnNamesAndAttributes]:
        return self.executeAndCommitSQLStatement("SELECT partID, InCarID, partName, taxesPaid, shippingCost, price FROM Parts", returnColumnNames=True)

    @autoSetHiddenColumnsByNames(["partID", "InCarID"])
    def getPartsForCar(self, carID: int) -> tuple[list, columnNamesAndAttributes]:
        return self.executeAndCommitSQLStatement("SELECT partID, InCarID, partName, taxesPaid, shippingCost, price FROM Parts WHERE InCarID = ?", placeholderValues=(carID,), returnColumnNames=True)

    @autoSetHiddenColumnsByNames(["employeeKey"])
    def getEmployees(self) -> tuple[list, columnNamesAndAttributes]:
        return self.executeAndCommitSQLStatement("SELECT employeeKey, employeeName FROM Employees", returnColumnNames=True)

    @autoSetHiddenColumnsByNames(["workEffortID", "carIDWorkedOn", "employeeWorkerKey"])
    def getWorkEfforts(self) -> tuple[list, columnNamesAndAttributes]:
        return self.executeAndCommitSQLStatement("SELECT workEffortID, carIDWorkedOn, employeeWorkerKey, workEffortDate, laborHours, estimatedPay, workType FROM WorkEfforts", returnColumnNames=True)

    @autoSetHiddenColumnsByNames(["workEffortID", "carIDWorkedOn", "employeeWorkerKey"])
    def getWorkEffortByCar(self, carID: int) -> tuple[list, columnNamesAndAttributes]:
        return self.executeAndCommitSQLStatement("""SELECT workEffortID, carIDWorkedOn, employeeWorkerKey, workEffortDate, laborHours, estimatedPay, workType 
                                                 FROM WorkEfforts 
                                                 WHERE CarIDWorkedOn = ?""", placeholderValues=(carID,), returnColumnNames=True)

    @autoSetHiddenColumnsByNames(["workEffortID", "carIDWorkedOn", "employeeWorkerKey"])
    def getWorkEffortByCarWithEmployees(self, carID: int):
        return self.executeAndCommitSQLStatement("""SELECT we.workEffortID, we.carIDWorkedOn, we.employeeWorkerKey, 
                                                 emp.EmployeeName, workEffortDate, laborHours, estimatedPay, workType 
                                                 FROM WorkEfforts we 
                                                 JOIN Employees emp 
                                                 ON we.employeeWorkerKey = emp.employeeKey 
                                                 WHERE we.CarIDWorkedOn = ?""",
                                                 placeholderValues=(carID,),
                                                 returnColumnNames=True)
    @staticmethod
    def CWI_SQL_flask_factory():
        """
        Factory for connecting to a database within a Flask application for a car work inventory application.
        :return: The instance of the car work inventory SQL database manager that's been stored in g.db
        """
        if 'db' not in g:
            g.db = carWorkInventorySQL(databaseName=DATABASE_FILE_PATH, rowFactory=carWorkInventorySQL.lowercaseKeyDictFactory)
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
                db.executeAndCommitSQLStatement(f.read().decode('utf-8'), IsScript=True)

            if use_test_data:
                with app.open_resource(TEST_DATA_FILE_PATH) as f:
                    db.executeAndCommitSQLStatement(f.read().decode('utf-8'), IsScript=True)

            db.connection.commit()