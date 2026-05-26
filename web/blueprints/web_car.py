# External Libraries or built-in Python libraries
from flask import Blueprint, render_template, redirect, url_for, g, request

# Modules / packages in this project
from helper import (addGAttr, replace_dict_empty_string_vals_with_none, addItemToDictionary,
                    setCarsTableAndInputConfig, setCarPartsTableAndInputConfig, setWorkEffortsByCarWithEmployeesTableAndInputConfig,
                    InputTypes)
from mappings import getTextMapping
from sql import carWorkInventorySQL
from common_helper import lowerCaseKeyDict

web_car = Blueprint('web_car', __name__, url_prefix='/car')

@web_car.route('/<int:keyorid>')
@addGAttr("textMap", getTextMapping)
@addGAttr("InputTypes", InputTypes.getInputTypes)
def car_page(keyorid):
    sqlapp = carWorkInventorySQL.CWI_SQL_flask_factory()

    partssqlresult = sqlapp.getPartsForCar(keyorid)
    setCarPartsTableAndInputConfig(partssqlresult[1])

    workeffortssqlresults = sqlapp.getWorkEffortByCarWithEmployees(keyorid)
    setWorkEffortsByCarWithEmployeesTableAndInputConfig(workeffortssqlresults[1],
                                                        sqlapp.getEmployees()[0])

    return render_template("car_view.html",
                           carssqlres=sqlapp.getCarById(keyorid),
                           partssqlres=partssqlresult,
                           workeffortssqlres=workeffortssqlresults)

@web_car.post('/<int:keyorid>')
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
            _ = sqlapp.insertPart(lowerCaseKeyDict(req_form_dict).lowercaseKeyDict)
        case "employees":
            raise NotImplementedError
        case "workefforts":
            req_form_dict = replace_dict_empty_string_vals_with_none(request.form)
            addItemToDictionary(req_form_dict, 'carIDWorkedOn', keyorid)
            _ = sqlapp.insertWorkEffort(lowerCaseKeyDict(req_form_dict).lowercaseKeyDict)
        case _:
            raise NotImplementedError
    partssqlresult = sqlapp.getPartsForCar(keyorid)
    setCarPartsTableAndInputConfig(partssqlresult[1])

    workeffortssqlresults = sqlapp.getWorkEffortByCarWithEmployees(keyorid)
    setWorkEffortsByCarWithEmployeesTableAndInputConfig(workeffortssqlresults[1],
                                                        sqlapp.getEmployees()[0])

    return render_template("car_view.html",
                           carssqlres=sqlapp.getCarById(keyorid),
                           partssqlres=partssqlresult,
                           workeffortssqlres=workeffortssqlresults)

@web_car.route('/edit/<int:keyorid>')
@addGAttr("textMap", getTextMapping)
@addGAttr("InputTypes", InputTypes.getInputTypes)
def car_edit_page(keyorid):
    # Opted for a separate web page as opposed to a modal from the main web page as this solution is easy to implement and will work for pretty much anyone
    # Where as a modal would most likely need javascript and javascript could be disabled for various reasons thus requiring more handling being implemented
    sqlapp = carWorkInventorySQL.CWI_SQL_flask_factory()

    carsSqlResult = sqlapp.getCarById(keyorid)
    setCarsTableAndInputConfig(carsSqlResult[1])

    return render_template("car_view.html",
                           carssqlres=carsSqlResult)

@web_car.post('/edit/<int:keyorid>')
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