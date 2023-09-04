from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, constr


class Sort(Enum):
    NAME = "name"
    DATE = "date"


class SortOrder(Enum):
    ASC = "asc"
    DESC = "desc"


class Error(BaseModel):
    code: str
    detail: str


class BasePostSchema(BaseModel):
    title: constr(strip_whitespace=True, min_length=1)
    body: constr(strip_whitespace=True, min_length=1)


class CreatePostSchema(BasePostSchema):
    pass


class PostSchema(BasePostSchema):
    id: UUID
    created: datetime
