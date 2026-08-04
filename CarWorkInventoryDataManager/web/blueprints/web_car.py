# External Libraries or built-in Python libraries
from flask import Blueprint, render_template, redirect, url_for, request

# Modules / packages in this project
from tableConfig import setWorkEffortsByCarWithEmployeesTableAndInputConfig, setItemsTableAndInputConfig, setCarsTableAndInputConfig, setCarsTableConfig, setPurchasesTableConfig, setValueEstimatesTableConfig, setItemGroupTransactionTableAndInputConfig
from db import get_CWI_db
from CarWorkInventoryDataManager.common_helper import lowerCaseKeyDict

web_car = Blueprint('web_car', __name__, url_prefix='/car')

@web_car.route('items/<int:keyorid>', methods=["GET", "POST"], endpoint="car_items")
@web_car.route('item-groups/<int:keyorid>', methods=["GET", "POST"], endpoint="car_igt")
def car_page(keyorid):
    sqlapp = get_CWI_db()

    igtFormTablePreFillData = []
    if request.method == "POST":
        match request.form["formid"].lower():
            case "items_form":
                req_form_dict = lowerCaseKeyDict(request.form)
                req_form_dict['incarkey'] = keyorid
                req_form_dict['itemgroupdescription'] = ""
                _ = sqlapp.insertSingleItem(req_form_dict)
                return redirect(url_for('.car_items', keyorid=keyorid))
            case "workefforts_form":
                req_form_dict = lowerCaseKeyDict(request.form)
                req_form_dict['carKeyWorkedOn'] = keyorid
                _ = sqlapp.insertWorkEffort(req_form_dict)
                return redirect(url_for(request.endpoint, keyorid=keyorid))
            case "igt_form":
                req_form_dict = lowerCaseKeyDict(request.form.to_dict(flat=False))
                tableData = []
                for columnName, valueList in req_form_dict.items():
                    if columnName in ('addnewrow', 'formid'):
                        continue

                    for index, value in enumerate(valueList):
                        if len(tableData) <= index:
                            tableData.append(lowerCaseKeyDict({columnName: value}))
                        else:
                            if columnName in tableData[index]:
                                raise ValueError(
                                    f"Unexpected Error: {columnName} already exists at row dictionary index: {index}")
                            tableData[index][columnName] = value

                if 'addnewrow' in req_form_dict:
                    igtFormTablePreFillData = tableData
                elif 'submit' in req_form_dict:
                    for itemDict in tableData:
                        itemDict['incarkey'] = keyorid

                    _ = sqlapp.insertMultipleItems(tableData)
                    return redirect(url_for('.car_igt', keyorid=keyorid))
                else:
                    raise NotImplementedError
            case _:
                raise NotImplementedError

    carssqlres = sqlapp.getCarByKey(keyorid)
    setCarsTableConfig(carssqlres[1])
    setPurchasesTableConfig(carssqlres[1], includeFooter=False)
    setValueEstimatesTableConfig(carssqlres[1])

    itemssqlresult = sqlapp.getItemsForCar(keyorid)
    setItemsTableAndInputConfig(itemssqlresult[1], True)

    igtsqlres = sqlapp.getItemsAndItemGroupTransactionsForCar(keyorid)
    setItemGroupTransactionTableAndInputConfig(igtsqlres[1])

    workeffortssqlresults = sqlapp.getWorkEffortByCarWithEmployees(keyorid)
    setWorkEffortsByCarWithEmployeesTableAndInputConfig(workeffortssqlresults[1],
                                                        sqlapp.getEmployees()[0])

    return render_template("car_view.html",
                           carssqlres=carssqlres,
                           itemssqlres=itemssqlresult,
                           igtsqlres=igtsqlres,
                           workeffortssqlres=workeffortssqlresults,
                           igtFormTablePreFillData=igtFormTablePreFillData)

@web_car.route('/edit/<int:keyorid>', methods=["GET", "POST"], endpoint="car_edit")
def car_edit_page(keyorid):
    # Opted for a separate web page as opposed to a modal from the main web page as this solution is easy to implement and will work for pretty much anyone
    # Where as a modal would most likely need javascript and javascript could be disabled for various reasons thus requiring more handling being implemented
    sqlapp = get_CWI_db()

    if request.method == "POST":
        req_form_dict = lowerCaseKeyDict(request.form)
        match request.form["formid"].lower():
            case "edit_car_form":
                req_form_dict['carkey'] = keyorid
                _ = sqlapp.updateCarAndValueEstimate(req_form_dict)
                return redirect(url_for('web_home.main_page'))
            case _:
                raise NotImplementedError

    carsSqlResult = sqlapp.getCarByKey(keyorid)
    setCarsTableAndInputConfig(carsSqlResult[1], includeFooter=False, includePurchaseData=False)

    return render_template("generic_table_form_view.html",
                           tablesqlres=carsSqlResult,
                           formId="edit_car",
                           legendText="Edit Car Entry",
                           prefillData=carsSqlResult[0][0])