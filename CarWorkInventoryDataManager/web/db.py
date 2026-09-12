from pathlib import Path
from flask import current_app, g

from CarWorkInventoryDataManager.sql import CWIDatabaseFactory

def get_CWI_db(useOnlyDatabaseURI=False):
    """
    Factory for connecting to a database within a Flask application for a car work inventory application.
    :return: An instance of the CWI Database object, should be the same instance across calls
    """
    if 'db' not in g:
        databaseURI = current_app.config['DATABASE_URI']
        g.db = CWIDatabaseFactory(Path(__file__).parent.parent.resolve() / databaseURI if not useOnlyDatabaseURI else databaseURI)

    return g.db

def db_teardown(exception):
    """
    Flask Teardown context handler for cleaning up the database connection/instance if it exists in a Flask application context
    :param exception: Exception provided by the Flask application teardown context
    :return: Nothing
    """
    db = g.pop('db', None)

    if db is not None:
        db.cleanup()

def setupDbInfrastructureForApp(app):
    app.teardown_appcontext(db_teardown)

def ensureCompleteData(func):
    """
    Decorator for ensuring that all data created or modified to the application database
    is only committed on success of the decorated function

    If the decorated function fails in any way,
    every modification made to the database is rolled back to the state before the function ran
    :param func: Function to be decorated that is used as part of a Flask application
    :return: The decorated function
    """
    def inner(*args, **kwargs):
        result = None
        with get_CWI_db().connection:
            result = func(*args, **kwargs)

        return result
    return inner

def backupDb():
    db = get_CWI_db()

    import datetime
    todayStr = datetime.datetime.now().strftime('%m-%d-%Y_%I-%M-%S')

    backupFileName = f"{todayStr}_CWIDb_Backup.db"
    backupFileLocation = Path(__file__).parent.parent.resolve() / "sql" / "databases" / "backups" / backupFileName
    backupDb = CWIDatabaseFactory(backupFileLocation)
    with backupDb.connection as backupTarget:
        db.connection.backup(backupTarget)

    db.cleanup()
    backupDb.cleanup()
    print(f"Backup complete at location: {backupFileLocation}")

