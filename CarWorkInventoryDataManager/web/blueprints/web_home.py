# External Libraries or built-in Python libraries
from flask import Blueprint, redirect, url_for, Response, request

# Modules / packages in this project
from ..tableConfig import setCarsWithViewEditLinksTableAndInputConfig, setEmployeesTableConfig, setItemsTableAndInputConfig
from CarWorkInventoryDataManager.common_helper import lowerCaseKeyDict
from ..viewclasses import getPostStandardViewBase
from ..datastructures.htmlEnums import InputTypes

web_home = Blueprint("web_home", __name__)

class homeView(getPostStandardViewBase):
    groupInputColumnsByResult = {"generalpurposesqlres": ["source", "itemName", "taxesPaid", "shippingCost", "cost", "refundAmount", "estimatedValue", "additionalNotes"]}
    def GET_Handler(self) -> dict:
        carssqlresult = self.sqlapp.getCarsWithViewEditLinksAndTotalValue()
        setCarsWithViewEditLinksTableAndInputConfig(carssqlresult[1])

        employeessqlresult = self.sqlapp.getEmployees()
        setEmployeesTableConfig(employeessqlresult[1])

        generalPurposeSqlResult = self.sqlapp.getGeneralPurposeItemsAndLinkedCars()
        setItemsTableAndInputConfig(generalPurposeSqlResult[1], True)
        generalPurposeCNA = generalPurposeSqlResult[1]
        generalPurposeCNA["itemKey"].isNestColumn = True
        generalPurposeCNA["source"].isNestColumn = True
        generalPurposeCNA["itemName"].isNestColumn = True
        generalPurposeCNA["purchaseKey"].isNestColumn = True
        generalPurposeCNA["taxesPaid"].isNestColumn = True
        generalPurposeCNA["shippingCost"].isNestColumn = True
        generalPurposeCNA["cost"].isNestColumn = True
        generalPurposeCNA["refundAmount"].isNestColumn = True
        generalPurposeCNA["purchaseTotal"].isNestColumn = True
        generalPurposeCNA["estimatedValue"].isNestColumn = True
        generalPurposeCNA["additionalNotes"].isNestColumn = True
        generalPurposeCNA["viewEditPurchaseDataLink"].isNestColumn = True

        for groupInputColumnName in homeView.groupInputColumnsByResult["generalpurposesqlres"]:
            generalPurposeCNA[groupInputColumnName].isGroupInput = True

        generalPurposeCNA["carKey"].InputType = InputTypes.DROPDOWN.value
        generalPurposeCNA["carKey"].requiredInput = True
        generalPurposeCNA["carKey"].dropDownData = ("carKey", self.sqlapp.getCars()[0], lambda row: f"{row["make"]} {row["model"]} {row["year"]} {row["engineType"]} mi:{row["mileage"]}", "carKey")

        self.viewSessionData.get("gpiPreFillData", [])

        return {"carssqlres" : carssqlresult,
                "employeessqlres": employeessqlresult,
                "generalpurposesqlres": generalPurposeSqlResult,
                "gpiPreFillData": self.viewSessionData.get("gpiPreFillData", []),
                "gpiFormTableIncludeNewRow": self.viewSessionData.get("gpiFormTableIncludeNewRow", True)}

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
            case "generalpurposeitems_form":
                def appendGeneralPurposeAndEmptyIgtDescription(tblData):
                    for row in tblData:
                        row["itemgroupdescription"] = ""
                        row["isgeneralpurpose"] = True

                self.tableEntryForm_Handler("gpiPreFillData",
                                            "gpiFormTableIncludeNewRow",
                                            "generalpurposesqlres",
                                            lambda tblData: self.sqlapp.insertGeneralPurposeItemWithOneOrMoreCarLinks(tblData),
                                            appendGeneralPurposeAndEmptyIgtDescription)
            case _:
                raise NotImplementedError
        return redirect(url_for('.main_page', _anchor=request.form["formid"].lower()))

web_home.add_url_rule("/", view_func=homeView.as_view("main_page", "index.html", "home"))