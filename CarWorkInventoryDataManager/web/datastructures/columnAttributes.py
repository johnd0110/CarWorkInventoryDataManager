from dataclasses import dataclass
from typing import Any

from CarWorkInventoryDataManager.common_helper import lowerCaseKeyDict
from datastructures import VisibilityOptions, InputTypes, WrapOptions
from CarWorkInventoryDataManager.sql.sql_infrastructure import columnNames

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
    InputAlias: An alias for the input form field name i.e. description -> itemGroupDescription, if None or empty string -> use column name
    MinMaxStep: A Tuple consisting of:
                A string representing the lower bound of the input type
                A string representing the upper bound of the input type
                A string representing the step of the input type i.e. 1 -> A numerical input should only ever contain values that are divisible by 1 (Integers)
    requiredInput: Whether the input is required (Sets a required attribute onto the input field)
    isNestColumn: If true, the column is used for creating nested result sets
                  where the nested result set consists of data rows
                  that share common values within all isNestColumn = True columns
                  within this result set
                  NOTE: This only allows for nested result sets with a depth level of 1
    makeTableHeader: Whether a table header should be made for the column. If false, an empty table header is made, otherwise a table header using the column's name is made.
    urlData: A tuple consisting of:
             A string representing the Flask View Function name to generate a URL for
             A string representing a default row value to show for the link in case there is no value in the sql data already.
             A string representing the columnName of the table from which a value should be retrieved for the row clicked from to be passed when the link is clicked
    wrap: WrapOptions value to set in a textarea element's wrap attribute. Defaults to soft. Only has an effect on textarea form inputs.
    footerTotalTextMapKey: A text map key to retrieve a decode for the generated footer total of this column.
                           Doubles as an indicator for if a footer total should be calculated and shown for the column
    decimalPlaces: The number of decimal places to display the values of the column with, only applies if the values are numbers
                   Also applies to footer totals
    default: Tuple of a value to compare and replace with default text and the default text to use
    isGroupInput: True if the given column should only be a form input that spans an entire grouped entry (Only one input of this kind for the whole group)
    """
    dropDownData: tuple[str, list, str] = None
    visibility: str = VisibilityOptions.INITIAL.value
    InputType: InputTypes = InputTypes.NOTINPUT.value
    InputAlias: str = None
    MinMaxStep: tuple[str, str, str] = None
    requiredInput: bool = False
    isNestColumn: bool = False
    makeTableHeader: bool = True
    urlData: tuple[str, str, str] = None
    wrap: WrapOptions = WrapOptions.SOFT.value
    footerTotalTextMapKey: str = ""
    decimalPlaces: int = 0
    default: tuple[Any, str] = None
    isGroupInput: bool = False

    def isFooterTotalColumn(self):
        return bool(self.footerTotalTextMapKey)

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

    def _getSubsetByFilterFunc(self, filterFunc):
        return self.from_columnnamesattributes_dict({columnName: colAttr for columnName, colAttr in self.items() if filterFunc((columnName, colAttr))})

    def getFooterTotalColumnsSubset(self):
        return self._getSubsetByFilterFunc(lambda item: item[1].isFooterTotalColumn())

    def getNestColumnsSubset(self, getOpposite: bool=False):
        return self._getSubsetByFilterFunc(lambda item: item[1].isNestColumn ^ getOpposite)

    def nestColumnExists(self, checkAll: bool=False):
        nestColumnBoolList = [colAttr.isNestColumn for colAttr in self.values()]
        return all(nestColumnBoolList) if checkAll else any(nestColumnBoolList)

    def generateColSpansAndFooterColumnNamesWithFiller(self):
        enumeratedVisibleColumnNames = list(enumerate(self.keys()))
        tableIndicesAndFooterColumnNames = [indexAndColumnNameTuple for indexAndColumnNameTuple in enumeratedVisibleColumnNames if self[indexAndColumnNameTuple[1]].isFooterTotalColumn()]

        colSpanAndFooterColumnNamesListWithFiller = []
        visibleColumnNamesListLength = len(enumeratedVisibleColumnNames)
        currentLength = 0
        for tableIndex, footerColumnName in tableIndicesAndFooterColumnNames:
            fillerColumnSpan = tableIndex - currentLength
            if fillerColumnSpan > 0:
                colSpanAndFooterColumnNamesListWithFiller.append((fillerColumnSpan, ""))
                currentLength += fillerColumnSpan

            colSpanAndFooterColumnNamesListWithFiller.append((1, footerColumnName))
            currentLength += 1

        if currentLength < visibleColumnNamesListLength:
            colSpanAndFooterColumnNamesListWithFiller.append((visibleColumnNamesListLength - currentLength, ""))
        elif currentLength > visibleColumnNamesListLength:
            raise ValueError(f"Unexpected Error: Size of list of column spans and names for footer exceeds visible column names list size.")

        return colSpanAndFooterColumnNamesListWithFiller

    def HasValidInputs(self):
        for columnName, attributes in self.items():
            if attributes.InputType == InputTypes.DROPDOWN.value and not attributes.HasValidDropDownData():
                return False

            if attributes.InputType not in InputTypes:
                return False

        return True

    @classmethod
    def from_columnnamesattributes_dict(cls, cna_dict: dict[str, columnWebAttributes]):
        intermediateobj = cls(list(cna_dict))
        for columnName, attributes in cna_dict.items():
            intermediateobj[columnName] = attributes
        return intermediateobj