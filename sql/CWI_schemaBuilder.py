from pathlib import Path

from carworkinvsql import CWIDatabaseFactory, SCHEMA_FILE_PATH

if __name__ == '__main__':
    """
    Run this to build out the database schema for the Car Work Inventory Data Manager. 
    NOTE: This will drop all relevant tables and thus delete existing data in those tables
    """
    yesno = input("WARNING: Continuing will delete all data from the database. Are you sure you want to continue and rebuild the database? (y/n) ")
    if yesno.lower() == 'y':
        setup_db = CWIDatabaseFactory("databases\\CWI_Database.db")

        # Disable authorizer to allow schema to be built out
        setup_db.connection.set_authorizer(None)


        with open(Path(__file__).parent / SCHEMA_FILE_PATH) as schemaFile:
            setup_db.executeAndCommitSQLStatement(schemaFile.read(), columnNamesClassWrapper=None, IsScript=True)
            setup_db.connection.commit()

        # Re-Enable to only allow standard sql actions to process
        setup_db.connection.set_authorizer(setup_db.CWISqlAuthorizerCallback)

        tables, _ = setup_db.executeAndCommitSQLStatement("SELECT * FROM sqlite_schema")
        for table in tables:
            print(table)