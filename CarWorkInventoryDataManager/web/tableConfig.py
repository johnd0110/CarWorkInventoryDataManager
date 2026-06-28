from CarWorkInventoryDataManager.sql.SQL_CONSTANTS import MIN_SQL_YEAR, MAX_SQL_YEAR, MINIMUM_SQL_DATE, MAXIMUM_SQL_DATE
from datastructures.htmlEnums import InputTypes

def setCarsTableAndInputConfig(carsSqlResult):
    carsSqlResult["make"].InputType = InputTypes.TEXT.value
    carsSqlResult["make"].requiredInput = True

    carsSqlResult["model"].InputType = InputTypes.TEXT.value
    carsSqlResult["model"].requiredInput = True

    carsSqlResult["year"].InputType = InputTypes.NUMBER.value
    carsSqlResult["year"].requiredInput = True
    carsSqlResult["year"].MinMaxStep = (str(MIN_SQL_YEAR), str(MAX_SQL_YEAR), "1")

    carsSqlResult["engineType"].InputType = InputTypes.TEXT.value
    carsSqlResult["engineType"].requiredInput = True

    carsSqlResult["mileage"].InputType = InputTypes.NUMBER.value
    carsSqlResult["mileage"].requiredInput = True
    carsSqlResult["mileage"].MinMaxStep = ("0", None, None)

    carsSqlResult["additionalNotes"].InputType = InputTypes.TEXTAREA.value

    setPurchasesTableAndInputConfig(carsSqlResult)

    setValueEstimatesTableAndInputConfig(carsSqlResult)

def setCarsWithViewEditLinksTableAndInputConfig(carsSqlResult):
    setCarsTableAndInputConfig(carsSqlResult)

    carsSqlResult["viewLink"].makeTableHeader = False
    carsSqlResult["viewLink"].urlData = ('web_car.car_page', 'View', 'carKey')

    carsSqlResult["editLink"].makeTableHeader = False
    carsSqlResult["editLink"].urlData = ('web_car.car_edit_page', 'Edit', 'carKey')

def setEmployeesTableConfig(employeesSqlResult):

    employeesSqlResult["employeeName"].InputType = InputTypes.TEXT.value
    employeesSqlResult["employeeName"].requiredInput = True

def setItemsTableAndInputConfig(itemssqlCNA):
    itemssqlCNA["source"].InputType = InputTypes.TEXT.value
    itemssqlCNA["source"].requiredInput = True

    itemssqlCNA["itemName"].InputType = InputTypes.TEXT.value
    itemssqlCNA["itemName"].requiredInput = True

    itemssqlCNA["additionalNotes"].InputType = InputTypes.TEXTAREA.value

    #TODO: Configure item group description fields
    setPurchasesTableAndInputConfig(itemssqlCNA)

    setValueEstimatesTableAndInputConfig(itemssqlCNA)

def setValueEstimatesTableAndInputConfig(sqlCNA):
    sqlCNA["estimatedValue"].InputType = InputTypes.NUMBER.value
    sqlCNA["estimatedValue"].requiredInput = False
    sqlCNA["estimatedValue"].MinMaxStep = ("0", None, "0.01")

def setPurchasesTableAndInputConfig(sqlCNA):
    sqlCNA["taxesPaid"].InputType = InputTypes.NUMBER.value
    sqlCNA["taxesPaid"].requiredInput = True
    sqlCNA["taxesPaid"].MinMaxStep = ("0", None, "0.01")

    sqlCNA["shippingCost"].InputType = InputTypes.NUMBER.value
    sqlCNA["shippingCost"].requiredInput = True
    sqlCNA["shippingCost"].MinMaxStep = ("0", None, "0.01")

    sqlCNA["cost"].InputType = InputTypes.NUMBER.value
    sqlCNA["cost"].requiredInput = True
    sqlCNA["cost"].MinMaxStep = (None, None, "0.01")

    sqlCNA["refundAmount"].InputType = InputTypes.NUMBER.value
    sqlCNA["refundAmount"].requiredInput = True
    sqlCNA["refundAmount"].MinMaxStep = ("0", None, "0.01")

def setWorkEffortsByCarWithEmployeesTableAndInputConfig(workeffortssqlCNA, employeessqldata):
    workeffortssqlCNA["employeeKey"].isNestColumn = True

    workeffortssqlCNA["employeeName"].InputType = InputTypes.DROPDOWN.value
    workeffortssqlCNA["employeeName"].requiredInput = True
    workeffortssqlCNA["employeeName"].dropDownData = ("employeeKey", employeessqldata, "employeeKey")
    workeffortssqlCNA["employeeName"].isNestColumn = True

    workeffortssqlCNA["workEffortDate"].InputType = InputTypes.DATE.value
    workeffortssqlCNA["workEffortDate"].requiredInput = True
    workeffortssqlCNA["workEffortDate"].MinMaxStep = (str(MINIMUM_SQL_DATE.date()), str(MAXIMUM_SQL_DATE.date()), "1")

    workeffortssqlCNA["laborHours"].InputType = InputTypes.NUMBER.value
    workeffortssqlCNA["laborHours"].requiredInput = True
    workeffortssqlCNA["laborHours"].MinMaxStep = ("0", "24", "0.01")

    workeffortssqlCNA["estimatedPay"].InputType = InputTypes.NUMBER.value
    workeffortssqlCNA["estimatedPay"].requiredInput = True
    workeffortssqlCNA["estimatedPay"].MinMaxStep = ("0", None, "0.01")

    workeffortssqlCNA["workType"].InputType = InputTypes.TEXT.value
    workeffortssqlCNA["workType"].requiredInput = True