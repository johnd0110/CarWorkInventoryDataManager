from pathlib import Path
from flask import current_app, g

def get_CWI_db(useOnlyDatabaseURI=False):
    """
    Factory for connecting to a database within a Flask application for a car work inventory application.
    :return: An instance of the CWI Database object, should be the same instance across calls
    """
    if 'db' not in g:
        from CarWorkInventoryDataManager.sql import CWIDatabaseFactory
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