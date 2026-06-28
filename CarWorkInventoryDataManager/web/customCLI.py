import click
from flask import current_app, cli
from pathlib import Path

@click.command('initTestData')
@cli.with_appcontext
def initializeCWITestData():
    """
    Custom Flask CLI command to initialize test data into the database if app is in testing mode.
    Note: It deletes all existing data and populates the database with the test data as a clean slate.
    :return: None
    """
    if not current_app.config['TESTING']:
        print('Not testing environment, cancelling test data initialization.')
        return

    from db import get_CWI_db
    CWI_db = get_CWI_db()

    CWI_db.connection.set_authorizer(None)
    with current_app.open_resource(Path(__file__).parent.parent.resolve() / 'sql/test_data/manual_testing_data.sql', mode='rt', encoding='utf-8') as manual_test_data_script:
        CWI_db.executeSQLStatement(manual_test_data_script.read(), columnNamesClassWrapper=None, IsScript=True)
    CWI_db.connection.set_authorizer(CWI_db.CWISqlAuthorizerCallback)

@click.command('initDb')
@cli.with_appcontext
def initializeCWIDbSchema():
    """
    Run this to build out the database schema for the Car Work Inventory Data Manager.
    NOTE: This will drop all relevant tables and thus delete existing data in those tables
    :return: None
    """
    yesno = input("WARNING: Continuing will delete all data from the database. Are you sure you want to continue and rebuild the database? (y/n) ")
    if yesno.lower() == 'y':
        CWIManagerFilePath = Path(__file__).parent.parent.resolve()

        from CarWorkInventoryDataManager.sql import CWIDatabaseFactory
        setup_db = CWIDatabaseFactory(str(CWIManagerFilePath / "sql/databases/CWI_Database.db"))

        # Disable authorizer to allow schema to be built out
        setup_db.connection.set_authorizer(None)

        with open(CWIManagerFilePath / 'sql/schema/schema.sql') as schemaFile:
            setup_db.executeSQLStatement(schemaFile.read(), columnNamesClassWrapper=None, IsScript=True)
            setup_db.connection.commit()

        # Re-Enable to only allow standard sql actions to process
        setup_db.connection.set_authorizer(setup_db.CWISqlAuthorizerCallback)

        tables, _ = setup_db.executeSQLStatement("SELECT * FROM sqlite_schema")
        for table in tables:
            print(table)