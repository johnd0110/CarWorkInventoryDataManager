from dataclasses import dataclass
from itertools import groupby
from enum import StrEnum, unique

from sql import MIN_SQL_YEAR, MAX_SQL_YEAR, MINIMUM_SQL_DATE, MAXIMUM_SQL_DATE, columnNames
from common_helper import lowerCaseKeyDict

@unique
class InputTypes(StrEnum):
    NOTINPUT = ""
    TEXT = "text"
    DATE = "date"
    NUMBER = "number"
    DROPDOWN = "dropdown"

    @staticmethod
    def getInputTypes():
        return InputTypes

@unique
class VisibilityOptions(StrEnum):
    INITIAL = "initial"
    COLLAPSE = "collapse"

@dataclass
class columnWebAttributes:
    """
    Attributes for a dynamically built HTML table column.
    dropDownData: A Tuple consisting of:
                  The SQL Column Name to pull data and attach to a given dropdown selection,
                  The SQL data to pull the options from as well as the values to associate with the options,
                  The SQL Column Name to save the selected data to
    visibility: Visibility attribute to assign to the column
    InputType: A InputType Enum value to designate what kind of input to create on the HTML document if an input is needed
    MinMaxStep: A Tuple consisting of:
                A string representing the lower bound of the input type
                A string representing the upper bound of the input type
                A string representing the step of the input type i.e. 1 -> A numerical input should only ever contain values that are divisible by 1 (Integers)
    requiredInput: Whether the input is required (Sets a required attribute onto the input field)
    nestedOn: If the resulting table data should be grouped/nested on this column data
    nestPriority: The order in which the table nesting occurs
    makeTableHeader: Whether a table header should be made for the column. If false, an empty table header is made, otherwise a table header using the column's name is made.
    urlData: A tuple consisting of:
             A string representing the Flask View Function name to generate a URL for
             A string representing a default row value to show for the link in case there is no value in the sql data already.
             A string representing the columnName of the table from which a value should be retrieved for the row clicked from to be passed when the link is clicked
    """
    dropDownData: tuple[str, list, str] = None
    visibility: str = VisibilityOptions.INITIAL.value
    InputType: InputTypes = InputTypes.NOTINPUT.value
    MinMaxStep: tuple[str, str, str] = None
    requiredInput: bool = False
    nestedOn: bool = False
    nestPriority: int = -1
    makeTableHeader: bool = True
    urlData: tuple[str, str, str] = None

    def HasValidDropDownData(self):
        """
        Determines if the current instance of ColumnWebAttributes has a valid dropdown data.
        Valid drop down data is when we have some non-empty object for each element in the tuple.
        :return: True if the dropdown data is valid, False otherwise.
        """
        # May want to check if the sql column names in the data are valid columns, but I do not yet the cleanest method to do so.
        if not self.dropDownData: return False

        for item in self.dropDownData:
            if not item:
                return False
        return True

    def HasValidUrlData(self):
        if not self.urlData: return False

        for item in self.urlData:
            if not item:
                return False
        return True

class columnNamesAndAttributes(columnNames, lowerCaseKeyDict):

    def __init__(self, columnNamesList: list[str]):
        columnNames.__init__(self, columnNamesList)
        lowerCaseKeyDict.__init__(self, {oneColumnName: columnWebAttributes() for oneColumnName in self.columnNames})

    def getColumnsToNestOnOrderedByPriority(self):
        """
        Retrieves all column names with the web attribute nestedOn = True and sorts them in descending order by their assigned priority (Higher Value = Higher Priority)
        Then the columnNames are grouped by the priority value.
        :return: A list of tuples representing the grouped column names by priority, in order by priority and a plain list of all the columns with the nestedOn attribute = True
        """
        result = sorted([(columnName, attributes.nestPriority) for columnName, attributes in self.items() if attributes.nestedOn], key=lambda x: x[1], reverse=True)
        return [tuple([column[0] for column in group]) for _, group in groupby(result, lambda x: x[1])], [columnNameAttr[0] for columnNameAttr in result]

    def HasValidInputs(self):
        for columnName, attributes in self.items():
            if attributes.InputType == InputTypes.DROPDOWN.value and not attributes.HasValidDropDownData():
                return False

            if attributes.InputType not in InputTypes:
                return False

        return True

    @classmethod
    def from_columnnamesattributes_dict(cls, cna_dict: [str, columnWebAttributes]):
        intermediateobj = cls(list(cna_dict))
        for columnName, attributes in cna_dict.items():
            intermediateobj[columnName] = attributes
        return intermediateobj

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

    carsSqlResult["initialCost"].InputType = InputTypes.NUMBER.value
    carsSqlResult["initialCost"].requiredInput = True
    carsSqlResult["initialCost"].MinMaxStep = (None, None, "0.01")

def setCarsWithViewEditLinksTableAndInputConfig(carsSqlResult):
    setCarsTableAndInputConfig(carsSqlResult)

    carsSqlResult["viewLink"].makeTableHeader = False
    carsSqlResult["viewLink"].urlData = ('web_car.car_page', 'View', 'carID')

    carsSqlResult["editLink"].makeTableHeader = False
    carsSqlResult["editLink"].urlData = ('web_car.car_edit_page', 'Edit', 'carID')

def setEmployeesTableConfig(employeesSqlResult):

    employeesSqlResult["employeeName"].InputType = InputTypes.TEXT.value
    employeesSqlResult["employeeName"].requiredInput = True

def setCarPartsTableAndInputConfig(partssqlCNA):

    partssqlCNA["partName"].InputType = InputTypes.TEXT.value
    partssqlCNA["partName"].requiredInput = True

    partssqlCNA["taxesPaid"].InputType = InputTypes.NUMBER.value
    partssqlCNA["taxesPaid"].requiredInput = True
    partssqlCNA["taxesPaid"].MinMaxStep = ("0", None, "0.01")

    partssqlCNA["shippingCost"].InputType = InputTypes.NUMBER.value
    partssqlCNA["shippingCost"].requiredInput = True
    partssqlCNA["shippingCost"].MinMaxStep = ("0", None, "0.01")

    partssqlCNA["price"].InputType = InputTypes.NUMBER.value
    partssqlCNA["price"].requiredInput = True
    partssqlCNA["price"].MinMaxStep = (None, None, "0.01")

def setWorkEffortsByCarWithEmployeesTableAndInputConfig(workeffortssqlCNA, employeessqldata):
    workeffortssqlCNA["employeeWorkerKey"].nestedOn = True
    workeffortssqlCNA["employeeWorkerKey"].nestPriority = 100

    workeffortssqlCNA["employeeName"].InputType = InputTypes.DROPDOWN.value
    workeffortssqlCNA["employeeName"].requiredInput = True
    workeffortssqlCNA["employeeName"].dropDownData = ("employeeKey", employeessqldata, "employeeWorkerKey")
    workeffortssqlCNA["employeeName"].nestedOn = True
    workeffortssqlCNA["employeeName"].nestPriority = 100

    workeffortssqlCNA["workEffortDate"].InputType = InputTypes.DATE.value
    workeffortssqlCNA["workEffortDate"].requiredInput = True
    workeffortssqlCNA["workEffortDate"].MinMaxStep = (str(MINIMUM_SQL_DATE), str(MAXIMUM_SQL_DATE), "1")

    workeffortssqlCNA["laborHours"].InputType = InputTypes.NUMBER.value
    workeffortssqlCNA["laborHours"].requiredInput = True
    workeffortssqlCNA["laborHours"].MinMaxStep = ("0", "24", "0.01")

    workeffortssqlCNA["estimatedPay"].InputType = InputTypes.NUMBER.value
    workeffortssqlCNA["estimatedPay"].requiredInput = True
    workeffortssqlCNA["estimatedPay"].MinMaxStep = ("0", None, "0.01")

    workeffortssqlCNA["workType"].InputType = InputTypes.TEXT.value
    workeffortssqlCNA["workType"].requiredInput = True