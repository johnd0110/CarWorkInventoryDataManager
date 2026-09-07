from abc import ABC, abstractmethod

from flask.views import View
from flask import request, render_template, Response, session

from db import get_CWI_db, ensureCompleteData
# TODO: Validate that form data is submitted or user confirms that data will disappear when navigating away
class getPostStandardViewBase(ABC, View):
    methods = ["GET", "POST"]
    decorators = [ensureCompleteData]

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

    def dispatch_request(self):
        if request.method == "POST":
            return self.POST_Handler()

        return render_template(self.template, **self.GET_Handler())

    @abstractmethod
    def GET_Handler(self) -> dict:
        ...

    def POST_Handler(self) -> Response:
        raise NotImplementedError("Please implement this method in derived classes if a POST is being made.")

class getPostKeyViewBase(ABC, View):
    methods = ["GET", "POST"]
    decorators = [ensureCompleteData]

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

    def dispatch_request(self, key):
        if request.method == "POST":
            return self.POST_Handler(key)

        return render_template(self.template, **self.GET_Handler(key))

    @abstractmethod
    def GET_Handler(self, key) -> dict:
        ...

    def POST_Handler(self, key) -> Response:
        """
        POST request handler, not a required override, but if a post request is made,
        then this will return an error indicating that this needs to have an implementation
        :param form: Form data in a lowerCaseKeyDict instance with the data unflattened
        :param key: key provided as a url parameter
        :return: Flask Redirect response
        """
        raise NotImplementedError("Please implement this method in derived classes if a POST is being made.")