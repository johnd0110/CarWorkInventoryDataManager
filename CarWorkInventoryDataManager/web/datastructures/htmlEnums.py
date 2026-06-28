from enum import StrEnum, unique

@unique
class InputTypes(StrEnum):
    NOTINPUT = ""
    TEXT = "text"
    TEXTAREA = "textarea"
    DATE = "date"
    NUMBER = "number"
    DROPDOWN = "dropdown"

@unique
class VisibilityOptions(StrEnum):
    INITIAL = "initial"
    COLLAPSE = "collapse"

@unique
class WrapOptions(StrEnum):
    SOFT = "soft"
    HARD = "hard"
    OFF = "off"