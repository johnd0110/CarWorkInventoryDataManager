# External Libraries or built-in Python libraries
from flask import Blueprint, request, render_template

# Modules / packages in this project
from tableConfig import setCarsWithViewEditLinksTableAndInputConfig, setEmployeesTableConfig
from db import get_CWI_db
from CarWorkInventoryDataManager.common_helper import lowerCaseKeyDict

web_home = Blueprint("web_home", __name__)

@web_home.route('/')
def main_page():
    sqlapp = get_CWI_db()

    carssqlresult = sqlapp.getCarsWithViewEditLinksAndTotalValue()
    setCarsWithViewEditLinksTableAndInputConfig(carssqlresult[1])

    employeessqlresult = sqlapp.getEmployees()
    setEmployeesTableConfig(employeessqlresult[1])

    return render_template("index.html",
                           carssqlres=carssqlresult,
                           employeessqlres=employeessqlresult)

@web_home.post('/')
def main_page_post():
    sqlapp = get_CWI_db()
    req_form_dict = lowerCaseKeyDict(request.form)
    match request.form["formid"].lower():
        case "cars_form":
            _ = sqlapp.insertCar(req_form_dict)
        case "parts_form":
            raise NotImplementedError
        case "employees_form":
            _ = sqlapp.insertEmployee(req_form_dict)
        case "workefforts_form":
            raise NotImplementedError
        case _:
            raise NotImplementedError

    carsqlresult = sqlapp.getCarsWithViewEditLinksAndTotalValue()
    setCarsWithViewEditLinksTableAndInputConfig(carsqlresult[1])

    employeessqlresult = sqlapp.getEmployees()
    setEmployeesTableConfig(employeessqlresult[1])

    return render_template("index.html",
                           carssqlres=carsqlresult,
                           employeessqlres=employeessqlresult)