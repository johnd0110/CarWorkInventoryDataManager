from itertools import groupby
from collections.abc import Iterable

from CarWorkInventoryDataManager.common_helper import lowerCaseKeyDict

def groupSqlResultsByColumns(sqlresults, columnNames: Iterable[str]):
    """
    Flask template filter function that groups sql result data by the data under the columns of columnNames
    :param sqlresults: Sql result data (first element of the tuple returned by the executeAndCommitSQLStatement in sql_infrastructure)
    :param columnNames: An iterable of column name strings that should exist in sqlresults that will be used to group the sql result data
    :return: An iterator of elements that each contain the key the group was sorted on and the grouped data
    """
    keyFunc = lambda sqlrow: tuple([sqlrow[columnName] for columnName in columnNames])
    return [(lowerCaseKeyDict(dict(zip(columnNames, groupkey))), list(group)) for groupkey, group in groupby(sorted(sqlresults, key=keyFunc), keyFunc)]
