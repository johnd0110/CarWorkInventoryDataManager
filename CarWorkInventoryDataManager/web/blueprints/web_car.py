# External Libraries or built-in Python libraries
from flask import Blueprint, redirect, url_for, request, Response, session

# Modules / packages in this project
from tableConfig import setWorkEffortsByCarWithEmployeesTableAndInputConfig, setItemsTableAndInputConfig, setCarsTableAndInputConfig, setCarsTableConfig, setPurchasesTableConfig, setValueEstimatesTableConfig, setItemGroupTransactionTableAndInputConfig
from CarWorkInventoryDataManager.common_helper import lowerCaseKeyDict
from viewclasses import getPostKeyViewBase

web_car = Blueprint('web_car', __name__, url_prefix='/car')

class carView(getPostKeyViewBase):
    def GET_Handler(self, key) -> dict:
        carssqlres = self.sqlapp.getCarByKey(key)
        setCarsTableConfig(carssqlres[1])
        setPurchasesTableConfig(carssqlres[1], includeFooter=False)
        setValueEstimatesTableConfig(carssqlres[1])

        itemssqlresult = self.sqlapp.getItemsForCar(key)
        setItemsTableAndInputConfig(itemssqlresult[1], True)

        igtsqlres = self.sqlapp.getItemsAndItemGroupTransactionsForCar(key)
        setItemGroupTransactionTableAndInputConfig(igtsqlres[1])

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
                form = lowerCaseKeyDict(request.form.to_dict(flat=False))
                print(form)
                tableData = []
                for columnName, valueList in form.items():
                    if columnName in ('addnewrow', 'deleterow', 'formid'):
                        continue
                    print(columnName, valueList)
                    for index, value in enumerate(valueList):
                        if len(tableData) <= index:
                            tableData.append(lowerCaseKeyDict({columnName: value}))
                        else:
                            if columnName in tableData[index]:
                                raise ValueError(
                                    f"Unexpected Error: {columnName} already exists at row dictionary index: {index}")
                            tableData[index][columnName] = value

                redirectLocation = '.car_igt'
                if ('addnewrow' in form) ^ ('deleterow' in form):
                    # Convert lowercasekeydict to regular dictionaries for serialization
                    tableDataForSession = [rowdata.data for ind, rowdata in enumerate(tableData) if (int(form.get('deleterow', [-1])[0]) != ind)]
                    noSessionTableDataExists = len(tableDataForSession) == 0
                    if not noSessionTableDataExists:
                        # Shift the itemgroupdescription to the next row
                        igtDescription = None
                        for row in tableData:
                            if 'itemgroupdescription' in row:
                                igtDescription = row.pop('itemgroupdescription')

                        if igtDescription is None:
                            raise RuntimeError(
                                "Unexpected Error: No Item group description found while adding or deleting a row.")

                        tableDataForSession[0]['itemgroupdescription'] = igtDescription
                    # else Last row was deleted, therefore just let the table reset

                    self.viewSessionData["igtFormTablePreFillData"] = tableDataForSession
                    self.viewSessionData["igtFormTableIncludeNewRow"] = ('addnewrow' in form) or noSessionTableDataExists
                    session.modified = True
                elif 'submit' in form:
                    itemDictWithIgtDescriptionIndex = None
                    for index, itemDict in enumerate(tableData):
                        itemDict['carkey'] = key
                        if "itemgroupdescription" in itemDict:
                            if itemDictWithIgtDescriptionIndex is not None:
                                raise RuntimeError("Unexpected Error: Additional Item Group Transaction Item Row with a description found.")
                            itemDictWithIgtDescriptionIndex = index

                    # Make sure the row with the item group description is at the start of the list.
                    if itemDictWithIgtDescriptionIndex is None:
                        raise RuntimeError("Unexpected Error: No Item group transaction description found on form submission.")

                    tableData.insert(0, tableData.pop(itemDictWithIgtDescriptionIndex))

                    _ = self.sqlapp.insertMultipleItems(tableData)
                    _ = self.viewSessionData.pop('igtFormTablePreFillData', None)
                    _ = self.viewSessionData.pop('igtFormTableIncludeNewRow', None)
                    session.modified = True
                else:
                    raise NotImplementedError
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