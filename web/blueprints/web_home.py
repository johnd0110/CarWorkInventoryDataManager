# External Libraries or built-in Python libraries
from flask import Blueprint, request, render_template, g

# Modules / packages in this project
from sql import carWorkInventorySQL
from helper import (addGAttr,
                    setCarsWithViewEditLinksTableAndInputConfig, setEmployeesTableConfig,
                    InputTypes)
from mappings import getTextMapping
from common_helper import lowerCaseKeyDict

web_home = Blueprint("web_home", __name__)

@web_home.route('/')
@addGAttr("textMap", getTextMapping)
@addGAttr("InputTypes", InputTypes.getInputTypes)
def main_page():
    _ = carWorkInventorySQL.CWI_SQL_flask_factory()

    carssqlresult = g.db.getCarsWithViewEditLinksAndTotalValue()
    setCarsWithViewEditLinksTableAndInputConfig(carssqlresult[1])

    employeessqlresult = g.db.getEmployees()
    setEmployeesTableConfig(employeessqlresult[1])

    return render_template("index.html",
                           carssqlres=carssqlresult,
                           employeessqlres=employeessqlresult)

@web_home.post('/')
@addGAttr("textMap", getTextMapping)
@addGAttr("InputTypes", InputTypes.getInputTypes)
def main_page_post():
    sqlapp = carWorkInventorySQL.CWI_SQL_flask_factory()
    req_form_dict = lowerCaseKeyDict(request.form)
    match request.form["formid"].lower():
        case "cars":
            _ = sqlapp.insertCar(req_form_dict)
        case "parts":
            raise NotImplementedError
        case "employees":
            _ = sqlapp.insertEmployee(req_form_dict)
        case "workefforts":
            raise NotImplementedError
        case _:
            raise NotImplementedError

    carsqlresult = g.db.getCarsWithViewEditLinksAndTotalValue()
    setCarsWithViewEditLinksTableAndInputConfig(carsqlresult[1])

    employeessqlresult = g.db.getEmployees()
    setEmployeesTableConfig(employeessqlresult[1])

    return render_template("index.html",
                           carssqlres=carsqlresult,
                           employeessqlres=employeessqlresult)