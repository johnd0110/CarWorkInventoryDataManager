# External Libraries or built-in Python libraries
from flask import Blueprint, render_template, redirect, url_for, request

from conversion_helper import item
# Modules / packages in this project
from tableConfig import setWorkEffortsByCarWithEmployeesTableAndInputConfig, setItemsTableAndInputConfig, setCarsTableAndInputConfig
from db import get_CWI_db
from CarWorkInventoryDataManager.common_helper import lowerCaseKeyDict

web_car = Blueprint('web_car', __name__, url_prefix='/car')

@web_car.route('/<int:keyorid>')
def car_page(keyorid):
    #TODO: Set up item group transaction tables and fields
    sqlapp = get_CWI_db()

    itemssqlresult = sqlapp.getItemsForCar(keyorid)

    setItemsTableAndInputConfig(itemssqlresult[1])

    workeffortssqlresults = sqlapp.getWorkEffortByCarWithEmployees(keyorid)
    setWorkEffortsByCarWithEmployeesTableAndInputConfig(workeffortssqlresults[1],
                                                        sqlapp.getEmployees()[0])

    return render_template("car_view.html",
                           carssqlres=sqlapp.getCarById(keyorid),
                           itemssqlres=itemssqlresult,
                           workeffortssqlres=workeffortssqlresults)

@web_car.post('/<int:keyorid>')
def car_page_post(keyorid):
    sqlapp = get_CWI_db()

    match request.form["formid"].lower():
        case "items_form":
            req_form_dict = lowerCaseKeyDict(request.form)
            req_form_dict['incarkey'] = keyorid
            _ = sqlapp.insertItem(req_form_dict)
        case "workefforts_form":
            req_form_dict = lowerCaseKeyDict(request.form)
            req_form_dict['carKeyWorkedOn'] = keyorid
            _ = sqlapp.insertWorkEffort(req_form_dict)
        case _:
            raise NotImplementedError
    itemssqlresult = sqlapp.getItemsForCar(keyorid)
    setItemsTableAndInputConfig(itemssqlresult[1])

    workeffortssqlresults = sqlapp.getWorkEffortByCarWithEmployees(keyorid)
    setWorkEffortsByCarWithEmployeesTableAndInputConfig(workeffortssqlresults[1],
                                                        sqlapp.getEmployees()[0])

    return render_template("car_view.html",
                           carssqlres=sqlapp.getCarById(keyorid),
                           itemssqlres=itemssqlresult,
                           workeffortssqlres=workeffortssqlresults)

@web_car.route('/edit/<int:keyorid>')
def car_edit_page(keyorid):
    # Opted for a separate web page as opposed to a modal from the main web page as this solution is easy to implement and will work for pretty much anyone
    # Where as a modal would most likely need javascript and javascript could be disabled for various reasons thus requiring more handling being implemented
    sqlapp = get_CWI_db()

    carsSqlResult = sqlapp.getCarById(keyorid)
    setCarsTableAndInputConfig(carsSqlResult[1])

    return render_template("car_view.html",
                           carssqlres=carsSqlResult)

@web_car.post('/edit/<int:keyorid>')
def car_edit_page_post(keyorid):
    sqlapp = get_CWI_db()

    req_form_dict = lowerCaseKeyDict(request.form)
    match request.form["formid"].lower():
        case "edit_car_form":
            req_form_dict['carkey'] = keyorid
            _ = sqlapp.updateCarPurchaseAndValueEstimate(req_form_dict)
        case _:
            raise NotImplementedError

    return redirect(url_for('web_home.main_page'))