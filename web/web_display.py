from argparse import ArgumentError
import sqlite3
import sql.carworkinvsql
from sql.carworkinvsql import carWorkInventorySQL
from flask import Flask, render_template, request
from itertools import groupby

def addDropDownDataToColumnNameList(columnNameList: list[str], columnNamesAndDropDownData: dict[str: list[sqlite3.Row]] = None):
    if len(columnNameList) == 0:
        raise ArgumentError("Please provide at least one column name.")

    return {columnName.lower() : (None if columnNamesAndDropDownData is None else columnNamesAndDropDownData.get(columnName.lower())) for columnName in columnNameList}

def addItemToDictionary(dictionary, key, value):
    key = key.lower()
    if key in dictionary:
        raise ArgumentError("Duplicate key found")
    else:
        dictionary[key] = value

def replace_dict_empty_string_vals_with_none(dict):
    return { key : (None if val == '' else val) for key, val in dict.items()}

def initialize_app():
    """
    Initializes a Flask application with a car work inventory database.
    :return: The newly initialized Flask application
    """
    new_app = Flask(__name__)
    new_app.teardown_appcontext(carWorkInventorySQL.CWI_SQL_flask_teardown)
    carWorkInventorySQL.CWI_SQL_flask_initialize_db(new_app)
    return new_app

app = initialize_app()

@app.template_test('isHideColumnName')
def isHideColumnName(columnName: str):
    return columnName.lower().startswith(sql.carworkinvsql.HIDE_COLUMN_PREFIX)

@app.template_filter('groupSqlResultsByColumn')
def groupSqlResultsByColumn(sqlresults, columnName: str):
    print("yes", columnName)
    return groupby(sqlresults, lambda sqlrow: sqlrow[columnName])

@app.template_filter('getColumnVisiblityList')
def getColumnVisiblityList(columnNameList: list[str]):
    return ["collapse" if isHideColumnName(columnName) else "initial" for index, columnName in enumerate(columnNameList)]

@app.route('/')
def main_page():
    sqlapp = carWorkInventorySQL.CWI_SQL_flask_factory()
    carssqlresult, carstablecolumns = sqlapp.getCars()

    carstablecolumns = addDropDownDataToColumnNameList(carstablecolumns)

    employeessqlresult, employeestablecolumns = sqlapp.getEmployees()

    employeestablecolumns = addDropDownDataToColumnNameList(employeestablecolumns)


    return render_template("index.html",
                           carssqlres=carssqlresult,
                           carstablecolsdd=carstablecolumns,
                           employeessqlres=employeessqlresult,
                           employeestablecolsdd=employeestablecolumns)

@app.post('/')
def main_page_post():
    sqlapp = carWorkInventorySQL.CWI_SQL_flask_factory()
    #TODO: Handle when invalid values are provided to the INSERT
    match request.form["formid"].lower():
        case "cars":
            _ = sqlapp.executeAndCommitSQLStatement(
                "INSERT INTO Cars(make, model, year, engineType, mileage) VALUES (:make, :model, :year, :enginetype, :mileage)",
                replace_dict_empty_string_vals_with_none(request.form))
        case "parts":
            raise NotImplementedError
        case "employees":
            _ = sqlapp.executeAndCommitSQLStatement(
                "INSERT INTO Employees(employeeName) VALUES (:employeename)",
                replace_dict_empty_string_vals_with_none(request.form))
        case "workefforts":
            raise NotImplementedError
        case _:
            raise NotImplementedError

    carssqlresult, carstablecolumns = sqlapp.getCars()

    carstablecolumns = addDropDownDataToColumnNameList(carstablecolumns)

    employeessqlresult, employeestablecolumns = sqlapp.getEmployees()

    employeestablecolumns = addDropDownDataToColumnNameList(employeestablecolumns)

    return render_template("index.html",
                           carssqlres=carssqlresult,
                           carstablecolsdd=carstablecolumns,
                           employeessqlres=employeessqlresult,
                           employeestablecolsdd=employeestablecolumns)

@app.route('/car/<int:keyorid>')
def car_page(keyorid):
    sqlapp = carWorkInventorySQL.CWI_SQL_flask_factory()

    carssqlresult, carstablecolumns = sqlapp.getCarById(keyorid)

    carstablecolumns = addDropDownDataToColumnNameList(carstablecolumns)

    partssqlresult, partstablecolumns = sqlapp.getPartsForCar(keyorid)

    partstablecolumns = addDropDownDataToColumnNameList(partstablecolumns)

    employeessqlresult, _ = sqlapp.getEmployees()

    workeffortssqlresult, workeffortstablecolumns = sqlapp.getWorkEffortByCarWithEmployees(keyorid)

    workeffortstablecolumns = addDropDownDataToColumnNameList(workeffortstablecolumns, {"employeename": employeessqlresult})
    return render_template("car_view.html",
                           carssqlres=carssqlresult,
                           carstablecolsdd=carstablecolumns,
                           partssqlres=partssqlresult,
                           partstablecolsdd=partstablecolumns,
                           workeffortssqlres=workeffortssqlresult,
                           workeffortstablecolsdd=workeffortstablecolumns)

@app.post('/car/<int:keyorid>')
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
                req_form_dict)
        case "employees":
            raise NotImplementedError
        case "workefforts":
            req_form_dict = replace_dict_empty_string_vals_with_none(request.form)
            addItemToDictionary(req_form_dict, 'carIDWorkedOn', keyorid)
            _ = sqlapp.executeAndCommitSQLStatement(
                "INSERT INTO WorkEfforts(carIDWorkedOn, employeeWorkerKey, workEffortDate, laborHours, estimatedPay, workType) VALUES (:caridworkedon, :employeeworkerkey, :workeffortdate, laborhours, estimatedpay, worktype)",
                req_form_dict)
        case _:
            raise NotImplementedError

    carssqlresult, carstablecolumns = sqlapp.getCarById(keyorid)

    carstablecolumns = addDropDownDataToColumnNameList(carstablecolumns)

    partssqlresult, partstablecolumns = sqlapp.getPartsForCar(keyorid)

    partstablecolumns = addDropDownDataToColumnNameList(partstablecolumns)

    employeessqlresult, _ = sqlapp.getEmployees()

    workeffortssqlresult, workeffortstablecolumns = sqlapp.getWorkEffortByCarWithEmployees(keyorid)

    #TODO: Create a custom column data type for determining different attributes like whether it should have a drop down or is a required input
    workeffortstablecolumns = addDropDownDataToColumnNameList(workeffortstablecolumns, {"employeename": employeessqlresult})
    return render_template("car_view.html",
                           carssqlres=carssqlresult,
                           carstablecolsdd=carstablecolumns,
                           partssqlres=partssqlresult,
                           partstablecolsdd=partstablecolumns,
                           workeffortssqlres=workeffortssqlresult,
                           workeffortstablecolsdd=workeffortstablecolumns)