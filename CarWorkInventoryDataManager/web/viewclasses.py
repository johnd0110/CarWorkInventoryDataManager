from abc import ABC, abstractmethod
from collections.abc import Callable

from flask.views import View
from flask import request, render_template, Response, session

from .db import get_CWI_db, ensureCompleteData
from CarWorkInventoryDataManager.common_helper import lowerCaseKeyDict

class _viewAbstractBase(ABC):
    methods = ["GET", "POST"]
    decorators = [ensureCompleteData]
    groupInputColumnsByResult = None

    def __init__(self, template, sessionDataName):
        self.sqlapp = get_CWI_db()
        self.template = template
        self._sessionDataName = sessionDataName

        # clear out all other session data except for the current view's session data
        # and ensure the current view's session data is initialized
        sessionData = session.pop(self._sessionDataName, {})
        session.clear()
        self.viewSessionData = sessionData

    @property
    def viewSessionData(self):
        """ Get this view's session data """
        return session[self._sessionDataName]

    @viewSessionData.setter
    def viewSessionData(self, value):
        """ Set this view's session data using value and ensure session modified attribute is set """
        session[self._sessionDataName] = value
        session.modified = True

    @abstractmethod
    def GET_Handler(self) -> dict:
        ...

    def POST_Handler(self) -> Response:
        """
        POST request handler, not a required override, but if a post request is made,
        then this will return an error indicating that this needs to have an implementation
        :param form: Form data in a lowerCaseKeyDict instance with the data unflattened
        :param key: key provided as a url parameter
        :return: Flask Redirect response
        """
        raise NotImplementedError("Please implement this method in derived classes if a POST is being made.")

    def tableEntryForm_Handler(self,
                               formTablePreFillDataKeyName: str,
                               formTableIncludeNewRowKeyName: str,
                               sqlResultName: str,
                               submitDataCompleter: Callable[[list[lowerCaseKeyDict]], None],
                               submitDataAppender: Callable[[list[lowerCaseKeyDict]], None] | None = None):
        """
        Standard handler for table entry form submissions.
        Expects custom implementations from derived classes in the form of injected functions
        :param formTablePreFillDataKeyName: A key name for the session data storing the unsubmitted table data
        :param formTableIncludeNewRowKeyName: A key name for the session data storing whether to include an empty new row on completion
        :param sqlResultName: sql result name key to retrieve group input column names from derived class variable
        :param submitDataCompleter: Function Implementation on how the submission completion is performed (like a SQL insert using the table data)
        :param submitDataAppender: Function Implementation for appending data to each row of the table data, optional, when not provided, nothing is appended
        :return: Nothing
        """
        #TODO: Consider adding message flashing
        form = lowerCaseKeyDict(request.form.to_dict(flat=False))

        # Transform the form table data into a more understandable consumable list of table rows
        tableData = []
        for columnName, valueList in form.items():
            if columnName in ('addnewrow', 'deleterow', 'formid'):
                continue
            for index, value in enumerate(valueList):
                if len(tableData) <= index:
                    tableData.append(lowerCaseKeyDict({columnName: value}))
                else:
                    if columnName in tableData[index]:
                        raise ValueError(f"Unexpected Error: {columnName} already exists at row dictionary index: {index}")
                    tableData[index][columnName] = value

        groupInputRowIndex = None
        for index, rowDict in enumerate(tableData):
            if len(rowDict.keys() & self.__class__.groupInputColumnsByResult[sqlResultName]) > 0:
                if groupInputRowIndex is not None:
                    raise RuntimeError("Unexpected Error: Additional Row with group input found.")
                groupInputRowIndex = index

        if groupInputRowIndex is None:
            raise RuntimeError("Unexpected Error: No group input found on form submission.")

        tableData.insert(0, tableData.pop(groupInputRowIndex))

        if ('addnewrow' in form) ^ ('deleterow' in form):
            # Convert lowercasekeydict to regular dictionaries for serialization
            tableDataForSession = [rowdata.data for ind, rowdata in enumerate(tableData) if
                                   (int(form.get('deleterow', [-1])[0]) != ind)]
            noSessionTableDataExists = len(tableDataForSession) == 0
            if not noSessionTableDataExists:
                # Shift grouped input data to next row
                intermediateGroupInputDict = lowerCaseKeyDict()
                for groupInputColumnName in self.__class__.groupInputColumnsByResult[sqlResultName]:
                    intermediateGroupInputDict[groupInputColumnName] = tableData[0].pop(groupInputColumnName)

                if not intermediateGroupInputDict:
                    raise RuntimeError("Unexpected Error: No group inputs found while adding or deleting a row.")

                tableDataForSession[0] |= intermediateGroupInputDict

            # else Last row was deleted, therefore just let the table reset

            self.viewSessionData[formTablePreFillDataKeyName] = tableDataForSession
            self.viewSessionData[formTableIncludeNewRowKeyName] = ('addnewrow' in form) or noSessionTableDataExists
            session.modified = True
        elif 'submit' in form:
            if submitDataAppender is not None:
                submitDataAppender(tableData)

            submitDataCompleter(tableData)
            _ = self.viewSessionData.pop(formTablePreFillDataKeyName, None)
            _ = self.viewSessionData.pop(formTableIncludeNewRowKeyName, None)
            session.modified = True
        else:
            raise NotImplementedError


# TODO: Validate that form data is submitted or user confirms that data will disappear when navigating away
class getPostStandardViewBase(_viewAbstractBase, View):

    def __init__(self, template, sessionDataName):
        super().__init__(template, sessionDataName)

    def dispatch_request(self):
        if request.method == "POST":
            return self.POST_Handler()

        return render_template(self.template, **self.GET_Handler())

class getPostKeyViewBase(_viewAbstractBase, View):

    def __init__(self, template, sessionDataName):
        super().__init__(template, sessionDataName)

    def dispatch_request(self, key):
        if request.method == "POST":
            return self.POST_Handler(key)

        return render_template(self.template, **self.GET_Handler(key))