import sqlite3
from sql.sql_infrastructure import baseSQL
from flask import g

SCHEMA_FILE_PATH = "..\\sql\\schema\\schema.sql"
DATABASE_FILE_PATH = "sql\\databases\\CWI_Database.db"
HIDE_COLUMN_PREFIX = 'hide_'

class carWorkInventorySQL(baseSQL):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def getCars(self):
        return self.executeAndCommitSQLStatement("SELECT carID as HIDE_CarID, make, model, year, engineType, mileage FROM Cars", returnColumnNames=True)

    def getCarById(self, carID):
        return self.executeAndCommitSQLStatement("SELECT carID as HIDE_CarID, make, model, year, engineType, mileage FROM Cars WHERE carID = ?", (carID,), returnColumnNames=True)

    def getParts(self):
        return self.executeAndCommitSQLStatement("SELECT partID as HIDE_partID, InCarID as HIDE_InCarID, partName, taxesPaid, shippingCost, price FROM Parts", returnColumnNames=True)

    def getPartsForCar(self, carID):
        return self.executeAndCommitSQLStatement("SELECT partID as HIDE_partID, InCarID as HIDE_InCarID, partName, taxesPaid, shippingCost, price FROM Parts WHERE InCarID = ?", placeholderValues=(carID,), returnColumnNames=True)

    def getEmployees(self):
        return self.executeAndCommitSQLStatement("SELECT employeeKey as HIDE_employeeKey, employeeName FROM Employees", returnColumnNames=True)

    def getWorkEfforts(self):
        return self.executeAndCommitSQLStatement("SELECT workEffortID as HIDE_workEffortID, carIDWorkedOn as HIDE_carIDWorkedOn, employeeWorkerKey as HIDE, workEffortDate, laborHours, estimatedPay, workType FROM WorkEfforts", returnColumnNames=True)

    def getWorkEffortByCar(self, carID):
        return self.executeAndCommitSQLStatement("""SELECT workEffortID as HIDE_workEffortID, carIDWorkedOn as HIDE_carIDWorkedOn, employeeWorkerKey as HIDE_employeeWorkerKey, workEffortDate, laborHours, estimatedPay, workType 
                                                 FROM WorkEfforts 
                                                 WHERE CarIDWorkedOn = ?""", placeholderValues=(carID,), returnColumnNames=True)

    def getWorkEffortByCarWithEmployees(self, carID):
        return self.executeAndCommitSQLStatement("""SELECT we.workEffortID as HIDE_workEffortID, we.carIDWorkedOn as HIDE_carIDWorkedOn, we.employeeWorkerKey as HIDE_employeeWorkerKey, 
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
            g.db = carWorkInventorySQL(databaseName=DATABASE_FILE_PATH)
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
    def CWI_SQL_flask_initialize_db(app):
        """
        Initialization function for a car work inventory SQL database as part of a Flask application.
        :param app: A Flask application
        :return: Nothing
        """
        with app.app_context():
            db = carWorkInventorySQL.CWI_SQL_flask_factory()
            with app.open_resource(SCHEMA_FILE_PATH) as f:
                db.executeAndCommitSQLStatement(f.read().decode('utf-8'), IsScript=True)
            db.connection.commit()

    @staticmethod
    def stripHideColumnPrefix(columnName: str):
        return columnName.lstrip(HIDE_COLUMN_PREFIX)