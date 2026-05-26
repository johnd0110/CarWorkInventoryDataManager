from functools import wraps
from collections.abc import Callable
from flask import g


def addGAttr(attributeName: str, retrievalFunc: Callable) -> Callable:
    """
    Decorator to add an attribute called attributeName to the Flask g object (if it does not yet exist) with the value returned from retrievalFunc.
    :param attributeName: Name for the attribute created for the Flask g object
    :param retrievalFunc: Function that returns a value to store in the g.[attributeName] attribute
    :return: The decorated function as is but g has a new attribute.
    """

    def addGAttr_decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            if attributeName not in g:
                setattr(g, attributeName, retrievalFunc())
            return func(*args, **kwargs)

        return wrapper

    return addGAttr_decorator