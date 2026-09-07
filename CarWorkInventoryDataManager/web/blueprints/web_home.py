# External Libraries or built-in Python libraries
from flask import Blueprint, redirect, url_for, Response, request

# Modules / packages in this project
from tableConfig import setCarsWithViewEditLinksTableAndInputConfig, setEmployeesTableConfig
from CarWorkInventoryDataManager.common_helper import lowerCaseKeyDict
from viewclasses import getPostStandardViewBase

web_home = Blueprint("web_home", __name__)

class homeView(getPostStandardViewBase):
    def GET_Handler(self) -> dict:
        carssqlresult = self.sqlapp.getCarsWithViewEditLinksAndTotalValue()
        setCarsWithViewEditLinksTableAndInputConfig(carssqlresult[1])

        employeessqlresult = self.sqlapp.getEmployees()
        setEmployeesTableConfig(employeessqlresult[1])

        return {"carssqlres" : carssqlresult, "employeessqlres": employeessqlresult}

    def POST_Handler(self) -> Response:
        form = lowerCaseKeyDict(request.form.to_dict())
        match form["formid"].lower():
            case "cars_form":
                _ = self.sqlapp.insertCar(form)
            case "parts_form":
                raise NotImplementedError
            case "employees_form":
                _ = self.sqlapp.insertEmployee(form)
            case "workefforts_form":
                raise NotImplementedError
            case _:
                raise NotImplementedError
        return redirect(url_for('.main_page'))

web_home.add_url_rule("/", view_func=homeView.as_view("main_page", "index.html", "home"))