# External Libraries or built-in Python libraries
from flask import Flask
from itertools import groupby
from collections.abc import Iterable

# Modules / packages in this project
from sql import carWorkInventorySQL
from helper import columnNamesAndAttributes
from blueprints import web_car, web_home

def initialize_app():
    """
    Initializes a Flask application with a car work inventory database.
    :return: The newly initialized Flask application
    """
    new_app = Flask(__name__)
    new_app.teardown_appcontext(carWorkInventorySQL.CWI_SQL_flask_teardown)
    carWorkInventorySQL.CWI_SQL_flask_initialize_db(new_app, True)
    new_app.register_blueprint(web_car)
    new_app.register_blueprint(web_home)
    return new_app

app = initialize_app()

@app.template_filter('groupSqlResultsByColumns')
def groupSqlResultsByColumns(sqlresults, columnNames: Iterable[str]):
    """
    Flask template filter function that groups sql result data by the data under the columns of columnNames
    :param sqlresults: Sql result data (first element of the tuple returned by the executeAndCommitSQLStatement in sql_infrastructure)
    :param columnNames: An iterable of column name strings that should exist in sqlresults that will be used to group the sql result data
    :return: An iterator of elements that each contain the key the group was sorted on and the grouped data
    """
    keyFunc = lambda sqlrow: tuple([sqlrow[columnName] for columnName in columnNames])
    return groupby(sorted(sqlresults, key=keyFunc), keyFunc)

@app.template_filter('getNewSubsetByColumnNames')
def getNewSubsetByColumnNames(columnsAndAttributes: columnNamesAndAttributes, columnNamesToFilterBy: Iterable[str], include: bool = True):
    """

    :param columnsAndAttributes:
    :param columnNamesToFilterBy:
    :param include:
    :return:
    """
    lowerColumnNames = [columnName.lower() for columnName in columnNamesToFilterBy]
    resultDict = {}
    for columnName, attributes in columnsAndAttributes.items():
        if include:
            if columnName in lowerColumnNames:
                resultDict[columnName] = attributes
        else:
            if columnName not in lowerColumnNames:
                resultDict[columnName] = attributes

    return columnNamesAndAttributes.from_columnnamesattributes_dict(resultDict)