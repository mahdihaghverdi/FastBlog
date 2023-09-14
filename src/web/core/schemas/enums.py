from enum import Enum


class Sort(Enum):
    TITLE = "title"
    DATE = "date"


class SortOrder(Enum):
    ASC = "asc"
    DESC = "desc"
