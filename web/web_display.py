from argparse import ArgumentError
from typing import Any
from sql.carworkinvsql import carWorkInventorySQL
from sql.sql_infrastructure import lowerCaseKeyDict, columnNamesAndAttributes
from flask import Flask, render_template, request, g
from itertools import groupby
from collections.abc import Iterable
from mappings.textMap import textMapFactory

def addItemToDictionary(dictionary, key, value):
    key = key.lower()
    if key in dictionary:
        raise ArgumentError("Duplicate key found")
    else:
        dictionary[key] = value

def replace_dict_empty_string_vals_with_none(dictToModify: dict[str, Any]):
    return { key : (None if val == '' else val) for key, val in dictToModify.items()}

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
    return groupby(sqlresults, lambda sqlrow: tuple([sqlrow[columnName] for columnName in columnNames]))

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

@app.route('/')
def main_page():
    _ = textMapFactory()
    sqlapp = carWorkInventorySQL.CWI_SQL_flask_factory()

    carsSqlResult = sqlapp.getCars()
    carsSqlResult[1]["make"].canBeInput = True
    carsSqlResult[1]["make"].requiredInput = True

    carsSqlResult[1]["model"].canBeInput = True
    carsSqlResult[1]["model"].requiredInput = True

    carsSqlResult[1]["year"].canBeInput = True
    carsSqlResult[1]["year"].requiredInput = True

    carsSqlResult[1]["engineType"].canBeInput = True
    carsSqlResult[1]["engineType"].requiredInput = True

    carsSqlResult[1]["mileage"].canBeInput = True
    carsSqlResult[1]["mileage"].requiredInput = True

    carsSqlResult[1]["initialCost"].canBeInput = True
    carsSqlResult[1]["initialCost"].requiredInput = True

    employeesSqlResult = sqlapp.getEmployees()

    employeesSqlResult[1]["employeeName"].canBeInput = True
    employeesSqlResult[1]["employeeName"].requiredInput = True

    return render_template("index.html",
                           carssqlres=carsSqlResult,
                           employeessqlres=employeesSqlResult)

@app.post('/')
def main_page_post():
    _ = textMapFactory()
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

    carsSqlResult = sqlapp.getCars()
    carsSqlResult[1]["make"].canBeInput = True
    carsSqlResult[1]["make"].requiredInput = True

    carsSqlResult[1]["model"].canBeInput = True
    carsSqlResult[1]["model"].requiredInput = True

    carsSqlResult[1]["year"].canBeInput = True
    carsSqlResult[1]["year"].requiredInput = True

    carsSqlResult[1]["engineType"].canBeInput = True
    carsSqlResult[1]["engineType"].requiredInput = True

    carsSqlResult[1]["mileage"].canBeInput = True
    carsSqlResult[1]["mileage"].requiredInput = True

    carsSqlResult[1]["initialCost"].canBeInput = True
    carsSqlResult[1]["initialCost"].requiredInput = True

    employeesSqlResult = sqlapp.getEmployees()

    employeesSqlResult[1]["employeeName"].canBeInput = True
    employeesSqlResult[1]["employeeName"].requiredInput = True

    return render_template("index.html",
                           carssqlres=carsSqlResult,
                           employeessqlres=employeesSqlResult)

@app.route('/car/<int:keyorid>')
def car_page(keyorid):
    _ = textMapFactory()
    sqlapp = carWorkInventorySQL.CWI_SQL_flask_factory()

    partsSqlResult = sqlapp.getPartsForCar(keyorid)

    partsSqlResult[1]["partName"].canBeInput = True
    partsSqlResult[1]["partName"].requiredInput = True

    partsSqlResult[1]["taxesPaid"].canBeInput = True
    partsSqlResult[1]["taxesPaid"].requiredInput = True

    partsSqlResult[1]["shippingCost"].canBeInput = True
    partsSqlResult[1]["shippingCost"].requiredInput = True

    partsSqlResult[1]["price"].canBeInput = True
    partsSqlResult[1]["price"].requiredInput = True

    employeessqlresult = sqlapp.getEmployees()

    workeffortssqlresult = sqlapp.getWorkEffortByCarWithEmployees(keyorid)

    workeffortssqlresult[1]["employeeWorkerKey"].nestedOn = True
    workeffortssqlresult[1]["employeeWorkerKey"].nestPriority = 100

    workeffortssqlresult[1]["employeeName"].canBeInput = True
    workeffortssqlresult[1]["employeeName"].requiredInput = True
    workeffortssqlresult[1]["employeeName"].dropDownData = ("employeeKey", employeessqlresult[0], "employeeWorkerKey")
    workeffortssqlresult[1]["employeeName"].nestedOn = True
    workeffortssqlresult[1]["employeeName"].nestPriority = 100

    workeffortssqlresult[1]["workEffortDate"].canBeInput = True
    workeffortssqlresult[1]["workEffortDate"].requiredInput = True

    workeffortssqlresult[1]["laborHours"].canBeInput = True
    workeffortssqlresult[1]["laborHours"].requiredInput = True

    workeffortssqlresult[1]["estimatedPay"].canBeInput = True
    workeffortssqlresult[1]["estimatedPay"].requiredInput = True

    workeffortssqlresult[1]["workType"].canBeInput = True
    workeffortssqlresult[1]["workType"].requiredInput = True

    return render_template("car_view.html",
                           carssqlres=sqlapp.getCarById(keyorid),
                           partssqlres=partsSqlResult,
                           workeffortssqlres=workeffortssqlresult)

@app.post('/car/<int:keyorid>')
def car_page_post(keyorid):
    _ = textMapFactory()
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

    partsSqlResult = sqlapp.getPartsForCar(keyorid)

    partsSqlResult[1]["partName"].canBeInput = True
    partsSqlResult[1]["partName"].requiredInput = True

    partsSqlResult[1]["taxesPaid"].canBeInput = True
    partsSqlResult[1]["taxesPaid"].requiredInput = True

    partsSqlResult[1]["shippingCost"].canBeInput = True
    partsSqlResult[1]["shippingCost"].requiredInput = True

    partsSqlResult[1]["price"].canBeInput = True
    partsSqlResult[1]["price"].requiredInput = True

    employeessqlresult = sqlapp.getEmployees()

    workeffortssqlresult = sqlapp.getWorkEffortByCarWithEmployees(keyorid)

    workeffortssqlresult[1]["employeeWorkerKey"].nestedOn = True
    workeffortssqlresult[1]["employeeWorkerKey"].nestPriority = 100

    workeffortssqlresult[1]["employeeName"].canBeInput = True
    workeffortssqlresult[1]["employeeName"].requiredInput = True
    workeffortssqlresult[1]["employeeName"].dropDownData = ("employeeKey", employeessqlresult[0], "employeeWorkerKey")
    workeffortssqlresult[1]["employeeName"].nestedOn = True
    workeffortssqlresult[1]["employeeName"].nestPriority = 100

    workeffortssqlresult[1]["workEffortDate"].canBeInput = True
    workeffortssqlresult[1]["workEffortDate"].requiredInput = True

    workeffortssqlresult[1]["laborHours"].canBeInput = True
    workeffortssqlresult[1]["laborHours"].requiredInput = True

    workeffortssqlresult[1]["estimatedPay"].canBeInput = True
    workeffortssqlresult[1]["estimatedPay"].requiredInput = True

    workeffortssqlresult[1]["workType"].canBeInput = True
    workeffortssqlresult[1]["workType"].requiredInput = True

    return render_template("car_view.html",
                           carssqlres=sqlapp.getCarById(keyorid),
                           partssqlres=partsSqlResult,
                           workeffortssqlres=workeffortssqlresult)