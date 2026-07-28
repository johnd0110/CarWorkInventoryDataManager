from CarWorkInventoryDataManager.sql.SQL_CONSTANTS import MIN_SQL_YEAR, MAX_SQL_YEAR, MINIMUM_SQL_DATE, MAXIMUM_SQL_DATE
from datastructures.htmlEnums import InputTypes

def setCarsTableConfig(carsSqlResult):
    carsSqlResult["totalInvestedValue"].decimalPlaces = 2

def setCarsInputConfig(carsSqlResult):
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

def setCarsTableAndInputConfig(carsSqlResult, includeFooter=True):
    setCarsInputConfig(carsSqlResult)

    setCarsTableConfig(carsSqlResult)

    setPurchasesTableAndInputConfig(carsSqlResult, includeFooter)

    setValueEstimatesTableAndInputConfig(carsSqlResult)

def setCarsWithViewEditLinksTableAndInputConfig(carsSqlResult):
    setCarsTableAndInputConfig(carsSqlResult)

    carsSqlResult["viewLink"].makeTableHeader = False
    carsSqlResult["viewLink"].urlData = ('web_car.car_items', 'View', 'carKey')

    carsSqlResult["editLink"].makeTableHeader = False
    carsSqlResult["editLink"].urlData = ('web_car.car_edit', 'Edit', 'carKey')

def setEmployeesTableConfig(employeesSqlResult):
    employeesSqlResult["employeeName"].InputType = InputTypes.TEXT.value
    employeesSqlResult["employeeName"].requiredInput = True

def setItemGroupTransactionTableConfig(igtsqlCNA):
    igtsqlCNA["itemGroupTransactionKey"].isNestColumn = True

    igtsqlCNA["itemGroupDescription"].isNestColumn = True

def setItemGroupTransactionTableAndInputConfig(igtsqlCNA):
    setItemGroupTransactionTableConfig(igtsqlCNA)

    igtsqlCNA["itemGroupDescription"].InputType = InputTypes.TEXTAREA.value
    igtsqlCNA["itemGroupDescription"].requiredInput = True
    igtsqlCNA["itemGroupDescription"].isGroupInput = True

    setItemsTableAndInputConfig(igtsqlCNA, True)

def setItemsTableAndInputConfig(itemssqlCNA, includeFooter=False):
    itemssqlCNA["source"].InputType = InputTypes.TEXT.value
    itemssqlCNA["source"].requiredInput = True

    itemssqlCNA["itemName"].InputType = InputTypes.TEXT.value
    itemssqlCNA["itemName"].requiredInput = True

    itemssqlCNA["additionalNotes"].InputType = InputTypes.TEXTAREA.value

    setPurchasesTableAndInputConfig(itemssqlCNA)

    setValueEstimatesTableAndInputConfig(itemssqlCNA, includeFooter=includeFooter)

def setValueEstimatesTableConfig(sqlCNA, includeFooter=False):
    sqlCNA["estimatedValue"].decimalPlaces = 2
    sqlCNA["estimatedValue"].default = (None, "N/A")

    if includeFooter:
        sqlCNA["estimatedValue"].footerTotalTextMapKey = "footerTotalEstimatedValue"

def setValueEstimatesInputConfig(sqlCNA):
    sqlCNA["estimatedValue"].InputType = InputTypes.NUMBER.value
    sqlCNA["estimatedValue"].requiredInput = False
    sqlCNA["estimatedValue"].MinMaxStep = ("0", None, "0.01")

def setValueEstimatesTableAndInputConfig(sqlCNA, includeFooter=False):
    setValueEstimatesTableConfig(sqlCNA, includeFooter=includeFooter)

    setValueEstimatesInputConfig(sqlCNA)

def setGeneralPurchasesTableConfig(sqlCNA):
    sqlCNA["taxesPaid"].decimalPlaces = 2

    sqlCNA["shippingCost"].decimalPlaces = 2

    sqlCNA["cost"].decimalPlaces = 2

    sqlCNA["refundAmount"].decimalPlaces = 2

def setPurchasesTableConfig(sqlCNA, includeFooter=True):
    setGeneralPurchasesTableConfig(sqlCNA)

    setViewPurchaseHistoryLinkTableConfig(sqlCNA)

    if includeFooter:
        sqlCNA["purchaseTotal"].footerTotalTextMapKey = "footerTotalSpent"

    sqlCNA["purchaseTotal"].decimalPlaces = 2

def setPurchasesInputConfig(sqlCNA):
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

def setPurchasesTableAndInputConfig(sqlCNA, includeFooter=True):
    setPurchasesTableConfig(sqlCNA, includeFooter)

    setPurchasesInputConfig(sqlCNA)

def setWorkEffortsByCarWithEmployeesTableAndInputConfig(workeffortssqlCNA, employeessqldata):
    workeffortssqlCNA["employeeKey"].isNestColumn = True

    workeffortssqlCNA["employeeName"].InputType = InputTypes.DROPDOWN.value
    workeffortssqlCNA["employeeName"].requiredInput = True
    workeffortssqlCNA["employeeName"].dropDownData = ("employeeKey", employeessqldata, "employeeKey")
    workeffortssqlCNA["employeeName"].isNestColumn = True

    workeffortssqlCNA["workEffortDate"].InputType = InputTypes.DATE.value
    workeffortssqlCNA["workEffortDate"].requiredInput = True
    workeffortssqlCNA["workEffortDate"].MinMaxStep = (str(MINIMUM_SQL_DATE.date()), str(MAXIMUM_SQL_DATE.date()), "1")
    workeffortssqlCNA["workEffortDate"].default = (str(MAXIMUM_SQL_DATE.date()), "N/A")

    workeffortssqlCNA["laborHours"].InputType = InputTypes.NUMBER.value
    workeffortssqlCNA["laborHours"].requiredInput = True
    workeffortssqlCNA["laborHours"].MinMaxStep = ("0", "24", "0.01")
    workeffortssqlCNA["laborHours"].decimalPlaces = 2

    workeffortssqlCNA["estimatedPay"].InputType = InputTypes.NUMBER.value
    workeffortssqlCNA["estimatedPay"].requiredInput = True
    workeffortssqlCNA["estimatedPay"].MinMaxStep = ("0", None, "0.01")
    workeffortssqlCNA["estimatedPay"].decimalPlaces = 2
    workeffortssqlCNA["estimatedPay"].footerTotalTextMapKey = "footerTotalPay"

    workeffortssqlCNA["workType"].InputType = InputTypes.TEXT.value
    workeffortssqlCNA["workType"].requiredInput = True

def setPurchaseHistoryTableConfig(sqlCNA):
    setGeneralPurchasesTableConfig(sqlCNA)

def setViewPurchaseHistoryLinkTableConfig(sqlCNA):
    sqlCNA["viewPurchaseHistoryLink"].makeTableHeader = False
    sqlCNA["viewPurchaseHistoryLink"].urlData = ('web_purchase_data.purchase_history_page', 'View Purchase History', 'purchaseKey')