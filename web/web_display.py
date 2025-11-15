from argparse import ArgumentError
from typing import Any
from sql.carworkinvsql import carWorkInventorySQL
from sql.sql_infrastructure import lowerCaseKeyDict, columnNamesAndAttributes, InputTypes
from sql.SQL_Constants import MINIMUM_SQL_DATE, MAXIMUM_SQL_DATE, MIN_SQL_YEAR, MAX_SQL_YEAR
from flask import Flask, render_template, request, g, redirect, url_for
from itertools import groupby
from collections.abc import Iterable, Callable
from mappings.textMap import getTextMapping
from functools import wraps

def addGAttr(attributeName: str, retrievalFunc: Callable) -> Callable:
    """
    Decorator to add an attribute called attributeName to the Flask g object (if it does not yet exist) with the value returned from retrievalFunc.
    :param attributeName: Name for the attribute created for the Flask g object
    :param retrievalFunc: Function that returns a value to store in the g.[attributeName] attribute
    :return: The decorated function as is but g has a new attribute.
    """
    def addGAttr_decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if attributeName not in g:
                setattr(g, attributeName, retrievalFunc())
            return func(*args, **kwargs)
        return wrapper
    return addGAttr_decorator

def addItemToDictionary(dictionary, key, value):
    key = key.lower()
    if key in dictionary:
        raise ArgumentError(message="Duplicate key found")
    else:
        dictionary[key] = value

def replace_dict_empty_string_vals_with_none(dictToModify: dict[str, Any]):
    return {key : (None if val == '' else val) for key, val in dictToModify.items()}

def initialize_app():
    """
    Initializes a Flask application with a car work inventory database.
    :return: The newly initialized Flask application
    """
    new_app = Flask(__name__)
    new_app.teardown_appcontext(carWorkInventorySQL.CWI_SQL_flask_teardown)
    carWorkInventorySQL.CWI_SQL_flask_initialize_db(new_app, True)
    return new_app

app = initialize_app()

@app.template_filter('groupSqlResultsByColumns')
def groupSqlResultsByColumns(sqlresults, columnNames: Iterable[str]):
    keyFunc = lambda sqlrow: tuple([sqlrow[columnName] for columnName in columnNames])
    return groupby(sorted(sqlresults, key=keyFunc), keyFunc)

@app.template_filter('getNewSubsetByColumnNames')
def getNewSubsetByColumnNames(columnsAndAttributes, columnNamesToFilterBy: Iterable[str], include: bool = True):
    lowerColumnNames = [columnName.lower() for columnName in columnNamesToFilterBy]
    resultDict = {}
    for columnName, attributes in columnsAndAttributes.items():
        if include:
            if columnName in lowerColumnNames:
                resultDict[columnName] = attributes
        else:
            if columnName not in lowerColumnNames:
                resultDict[columnName] = attributes

    return columnNamesAndAttributes(resultDict)

def setCarsInputAttributes(carsSqlResult):
    carsSqlResult[1]["make"].InputType = InputTypes.TEXT.value
    carsSqlResult[1]["make"].requiredInput = True

    carsSqlResult[1]["model"].InputType = InputTypes.TEXT.value
    carsSqlResult[1]["model"].requiredInput = True

    carsSqlResult[1]["year"].InputType = InputTypes.NUMBER.value
    carsSqlResult[1]["year"].requiredInput = True
    carsSqlResult[1]["year"].MinMaxStep = (str(MIN_SQL_YEAR), str(MAX_SQL_YEAR), "1")

    carsSqlResult[1]["engineType"].InputType = InputTypes.TEXT.value
    carsSqlResult[1]["engineType"].requiredInput = True

    carsSqlResult[1]["mileage"].InputType = InputTypes.NUMBER.value
    carsSqlResult[1]["mileage"].requiredInput = True
    carsSqlResult[1]["mileage"].MinMaxStep = ("0", None, None)

    carsSqlResult[1]["initialCost"].InputType = InputTypes.NUMBER.value
    carsSqlResult[1]["initialCost"].requiredInput = True
    carsSqlResult[1]["initialCost"].MinMaxStep = (None, None, "0.01")

def generateCarsWithViewEditLinksTableData():
    carsSqlResult = g.db.getCarsWithViewEditLinks()

    setCarsInputAttributes(carsSqlResult)

    carsSqlResult[1]["viewLink"].makeTableHeader = False
    carsSqlResult[1]["viewLink"].urlData = ('car_page', 'View', 'carID')

    carsSqlResult[1]["editLink"].makeTableHeader = False
    carsSqlResult[1]["editLink"].urlData = ('car_edit_page', 'Edit', 'carID')

    return carsSqlResult

def generateEmployeesTableData():
    employeesSqlResult = g.db.getEmployees()

    employeesSqlResult[1]["employeeName"].InputType = InputTypes.TEXT.value
    employeesSqlResult[1]["employeeName"].requiredInput = True

    return employeesSqlResult

@app.route('/')
@addGAttr("textMap", getTextMapping)
@addGAttr("InputTypes", InputTypes.getInputTypes)
def main_page():
    _ = carWorkInventorySQL.CWI_SQL_flask_factory()

    return render_template("index.html",
                           carssqlres=generateCarsWithViewEditLinksTableData(),
                           employeessqlres=generateEmployeesTableData())

@app.post('/')
@addGAttr("textMap", getTextMapping)
@addGAttr("InputTypes", InputTypes.getInputTypes)
def main_page_post():
    sqlapp = carWorkInventorySQL.CWI_SQL_flask_factory()
    #TODO: Handle when invalid values are provided to the INSERT
    match request.form["formid"].lower():
        case "cars":
            _ = sqlapp.executeAndCommitSQLStatement(
                "INSERT INTO Cars(make, model, year, engineType, mileage, initialcost) VALUES (:make, :model, :year, :enginetype, :mileage, :initialcost)",
                lowerCaseKeyDict(replace_dict_empty_string_vals_with_none(request.form)).lowercaseKeyDict)
        case "parts":
            raise NotImplementedError
        case "employees":
            _ = sqlapp.executeAndCommitSQLStatement(
                "INSERT INTO Employees(employeeName) VALUES (:employeename)",
                lowerCaseKeyDict(replace_dict_empty_string_vals_with_none(request.form)).lowercaseKeyDict)
        case "workefforts":
            raise NotImplementedError
        case _:
            raise NotImplementedError

    return render_template("index.html",
                           carssqlres=generateCarsWithViewEditLinksTableData(),
                           employeessqlres=generateEmployeesTableData())

def generatePartsForCarTableData(carID):
    partsSqlResult = g.db.getPartsForCar(carID)

    partsSqlResult[1]["partName"].InputType = InputTypes.TEXT.value
    partsSqlResult[1]["partName"].requiredInput = True

    partsSqlResult[1]["taxesPaid"].InputType = InputTypes.NUMBER.value
    partsSqlResult[1]["taxesPaid"].requiredInput = True
    partsSqlResult[1]["taxesPaid"].MinMaxStep = ("0", None, "0.01")

    partsSqlResult[1]["shippingCost"].InputType = InputTypes.NUMBER.value
    partsSqlResult[1]["shippingCost"].requiredInput = True
    partsSqlResult[1]["shippingCost"].MinMaxStep = ("0", None, "0.01")

    partsSqlResult[1]["price"].InputType = InputTypes.NUMBER.value
    partsSqlResult[1]["price"].requiredInput = True
    partsSqlResult[1]["price"].MinMaxStep = (None, None, "0.01")

    return partsSqlResult

def generateWorkEffortsByCarWithEmployeesTableData(carID):
    workeffortssqlresult = g.db.getWorkEffortByCarWithEmployees(carID)

    employeessqlresult = g.db.getEmployees()

    workeffortssqlresult[1]["employeeWorkerKey"].nestedOn = True
    workeffortssqlresult[1]["employeeWorkerKey"].nestPriority = 100

    workeffortssqlresult[1]["employeeName"].InputType = InputTypes.DROPDOWN.value
    workeffortssqlresult[1]["employeeName"].requiredInput = True
    workeffortssqlresult[1]["employeeName"].dropDownData = ("employeeKey", employeessqlresult[0], "employeeWorkerKey")
    workeffortssqlresult[1]["employeeName"].nestedOn = True
    workeffortssqlresult[1]["employeeName"].nestPriority = 100

    workeffortssqlresult[1]["workEffortDate"].InputType = InputTypes.DATE.value
    workeffortssqlresult[1]["workEffortDate"].requiredInput = True
    workeffortssqlresult[1]["workEffortDate"].MinMaxStep = (str(MINIMUM_SQL_DATE), str(MAXIMUM_SQL_DATE), "1")

    workeffortssqlresult[1]["laborHours"].InputType = InputTypes.NUMBER.value
    workeffortssqlresult[1]["laborHours"].requiredInput = True
    workeffortssqlresult[1]["laborHours"].MinMaxStep = ("0", "24", "0.01")

    workeffortssqlresult[1]["estimatedPay"].InputType = InputTypes.NUMBER.value
    workeffortssqlresult[1]["estimatedPay"].requiredInput = True
    workeffortssqlresult[1]["estimatedPay"].MinMaxStep = ("0", None, "0.01")

    workeffortssqlresult[1]["workType"].InputType = InputTypes.TEXT.value
    workeffortssqlresult[1]["workType"].requiredInput = True

    return workeffortssqlresult

@app.route('/car/<int:keyorid>')
@addGAttr("textMap", getTextMapping)
@addGAttr("InputTypes", InputTypes.getInputTypes)
def car_page(keyorid):
    sqlapp = carWorkInventorySQL.CWI_SQL_flask_factory()

    return render_template("car_view.html",
                           carssqlres=sqlapp.getCarById(keyorid),
                           partssqlres=generatePartsForCarTableData(keyorid),
                           workeffortssqlres=generateWorkEffortsByCarWithEmployeesTableData(keyorid))

@app.post('/car/<int:keyorid>')
@addGAttr("textMap", getTextMapping)
@addGAttr("InputTypes", InputTypes.getInputTypes)
def car_page_post(keyorid):
    sqlapp = carWorkInventorySQL.CWI_SQL_flask_factory()

    match request.form["formid"].lower():
        case "cars":
            raise NotImplementedError
        case "parts":
            req_form_dict = replace_dict_empty_string_vals_with_none(request.form)
            addItemToDictionary(req_form_dict, 'incarid', keyorid)
            _ = sqlapp.executeAndCommitSQLStatement(
                "INSERT INTO Parts(InCarID, partName, taxesPaid, shippingCost, price) VALUES (:incarid, :partname, :taxespaid, :shippingcost, :price)",
                lowerCaseKeyDict(req_form_dict).lowercaseKeyDict)
        case "employees":
            raise NotImplementedError
        case "workefforts":
            req_form_dict = replace_dict_empty_string_vals_with_none(request.form)
            addItemToDictionary(req_form_dict, 'carIDWorkedOn', keyorid)
            _ = sqlapp.executeAndCommitSQLStatement(
                "INSERT INTO WorkEfforts(carIDWorkedOn, employeeWorkerKey, workEffortDate, laborHours, estimatedPay, workType) VALUES (:caridworkedon, :employeeworkerkey, :workeffortdate, :laborhours, :estimatedpay, :worktype)",
                lowerCaseKeyDict(req_form_dict).lowercaseKeyDict)
        case _:
            raise NotImplementedError

    return render_template("car_view.html",
                           carssqlres=sqlapp.getCarById(keyorid),
                           partssqlres=generatePartsForCarTableData(keyorid),
                           workeffortssqlres=generateWorkEffortsByCarWithEmployeesTableData(keyorid))

@app.route('/car/edit/<int:keyorid>')
@addGAttr("textMap", getTextMapping)
@addGAttr("InputTypes", InputTypes.getInputTypes)
def car_edit_page(keyorid):
    # Opted for a separate web page as opposed to a modal from the main web page as this solution is easy to implement and will work for pretty much anyone
    # Where as a modal would most likely need javascript and javascript could be disabled for various reasons thus requiring more handling being implemented
    sqlapp = carWorkInventorySQL.CWI_SQL_flask_factory()

    carsSqlResult = sqlapp.getCarById(keyorid)
    setCarsInputAttributes(carsSqlResult)

    return render_template("car_view.html",
                           carssqlres=carsSqlResult)

@app.post('/car/edit/<int:keyorid>')
@addGAttr("textMap", getTextMapping)
@addGAttr("InputTypes", InputTypes.getInputTypes)
def car_edit_page_post(keyorid):
    sqlapp = carWorkInventorySQL.CWI_SQL_flask_factory()

    match request.form["formid"].lower():
        case "edit_car":
            req_form_dict = replace_dict_empty_string_vals_with_none(request.form)
            addItemToDictionary(req_form_dict, 'carid', keyorid)
            _ = sqlapp.executeAndCommitSQLStatement("UPDATE Cars SET make = :make, model = :model, year = :year, engineType = :enginetype, mileage = :mileage, initialCost = :initialcost WHERE carID = :carid", req_form_dict)
        case _:
            raise NotImplementedError

    return redirect(url_for('main_page'))


