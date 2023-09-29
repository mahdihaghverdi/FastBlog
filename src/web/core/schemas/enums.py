from enum import Enum


class Sort(Enum):
    TITLE = "title"
    DATE = "date"


class ReplyLevel(Enum):
    BASE = "0"
    ONE = "1"
    TWO = "2"
    THREE = "3"
