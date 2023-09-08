from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, constr


class Sort(Enum):
    TITLE = "title"
    DATE = "date"


class SortOrder(Enum):
    ASC = "asc"
    DESC = "desc"


class Error(BaseModel):
    code: str
    detail: str


class CreatePostSchema(BaseModel):
    title: constr(strip_whitespace=True, min_length=1)
    body: constr(strip_whitespace=True, min_length=1)


class PostSchema(BaseModel):
    id: UUID
    created: datetime
    title: constr(strip_whitespace=True, min_length=1)
    body: constr(strip_whitespace=True, min_length=1)


class Token(BaseModel):
    access_token: str
    token_type: str


class UserSchema(BaseModel):
    username: str
    posts: list[PostSchema]


class UserInDBSchema(UserSchema):
    password: str
