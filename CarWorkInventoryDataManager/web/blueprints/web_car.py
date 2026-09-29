# External Libraries or built-in Python libraries
from flask import Blueprint, redirect, url_for, request, Response, session

# Modules / packages in this project
from ..tableConfig import setWorkEffortsByCarWithEmployeesTableAndInputConfig, setItemsTableAndInputConfig, setCarsTableAndInputConfig, setCarsTableConfig, setPurchasesTableConfig, setValueEstimatesTableConfig
from CarWorkInventoryDataManager.common_helper import lowerCaseKeyDict
from ..viewclasses import getPostKeyViewBase
from ..datastructures.htmlEnums import InputTypes

web_car = Blueprint('web_car', __name__, url_prefix='/car')

class carView(getPostKeyViewBase):
    groupInputColumnsByResult = {"igtsqlres": ["itemGroupDescription"]}
    def GET_Handler(self, key) -> dict:
        carssqlres = self.sqlapp.getCarByKey(key)
        setCarsTableConfig(carssqlres[1])
        setPurchasesTableConfig(carssqlres[1], includeFooter=False)
        setValueEstimatesTableConfig(carssqlres[1])

        itemssqlresult = self.sqlapp.getItemsForCar(key)
        setItemsTableAndInputConfig(itemssqlresult[1], True)

        igtsqlres = self.sqlapp.getItemsAndItemGroupTransactionsForCar(key)
        igtsqlCNA = igtsqlres[1]
        igtsqlCNA["itemGroupTransactionKey"].isNestColumn = True

        igtsqlCNA["itemGroupDescription"].isNestColumn = True
        igtsqlCNA["itemGroupDescription"].InputType = InputTypes.TEXTAREA.value
        igtsqlCNA["itemGroupDescription"].requiredInput = True
        for groupInputColumnName in carView.groupInputColumnsByResult["igtsqlres"]:
            igtsqlCNA[groupInputColumnName].isGroupInput = True

        setItemsTableAndInputConfig(igtsqlCNA, True)

        workeffortssqlresults = self.sqlapp.getWorkEffortByCarWithEmployees(key)
        setWorkEffortsByCarWithEmployeesTableAndInputConfig(workeffortssqlresults[1],
                                                            self.sqlapp.getEmployees()[0])

        return {"carssqlres": carssqlres,
                "itemssqlres": itemssqlresult,
                "igtsqlres": igtsqlres,
                "workeffortssqlres": workeffortssqlresults,
                "igtFormTablePreFillData": self.viewSessionData.get("igtFormTablePreFillData", []),
                "igtFormTableIncludeNewRow": self.viewSessionData.get("igtFormTableIncludeNewRow", True)}

    def POST_Handler(self, key) -> Response:
        redirectLocation = ''
        form = lowerCaseKeyDict(request.form.to_dict())
        match form["formid"].lower():
            case "items_form":
                form['carkey'] = key
                form['itemgroupdescription'] = ""
                _ = self.sqlapp.insertSingleItem(form)
                redirectLocation = '.car_items'
            case "workefforts_form":
                form['carKeyWorkedOn'] = key
                _ = self.sqlapp.insertWorkEffort(form)
                redirectLocation = request.endpoint
            case "igt_form":
                redirectLocation = '.car_igt'

                def appendCarKey(tblData):
                    for row in tblData:
                        row["carKey"] = key

                self.tableEntryForm_Handler("igtFormTablePreFillData",
                                            "igtFormTableIncludeNewRow",
                                            "igtsqlres",
                                            lambda tblData: self.sqlapp.insertMultipleItems(tblData),
                                            appendCarKey)
            case _:
                raise NotImplementedError

        return redirect(url_for(redirectLocation, key=key, _anchor=request.form["formid"].lower()))

class carEditView(getPostKeyViewBase):
    def GET_Handler(self, key) -> dict:
        carsSqlResult = self.sqlapp.getCarByKey(key)
        setCarsTableAndInputConfig(carsSqlResult[1], includeFooter=False, includePurchaseData=False)

        return {"tablesqlres": carsSqlResult,
                "formId": "edit_car",
                "legendText": "Edit Car Entry",
                "prefillData": carsSqlResult[0][0]}

    def POST_Handler(self, key) -> Response:
        form = lowerCaseKeyDict(request.form.to_dict())
        match form["formid"].lower():
            case "edit_car_form":
                form['carkey'] = key
                _ = self.sqlapp.updateCarAndValueEstimate(form)
            case _:
                raise NotImplementedError

        return redirect(url_for('web_home.main_page'))

web_car.add_url_rule('items/<int:key>', endpoint="car_items", view_func=carView.as_view("car_page", "car_view.html", "car"))
web_car.add_url_rule('item-groups/<int:key>', endpoint="car_igt", view_func=carView.as_view("car_page", "car_view.html", "car"))
web_car.add_url_rule('/edit/<int:key>', endpoint="car_edit", view_func=carEditView.as_view("car_edit_page", "generic_table_form_view.html", "car_edit"))