from datetime import datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, constr, AnyHttpUrl


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
    title_in_url: constr(strip_whitespace=True, min_length=1) | None = None


class CreateDraftSchema(BaseModel):
    title: constr(strip_whitespace=True, min_length=1)
    body: constr(strip_whitespace=True, min_length=1)


class DraftSchema(BaseModel):
    id: UUID
    created: datetime
    title: constr(strip_whitespace=True, min_length=1)
    body: constr(strip_whitespace=True, min_length=1)


class PostSchema(BaseModel):
    id: UUID
    created: datetime
    title: constr(strip_whitespace=True, min_length=1)
    body: constr(strip_whitespace=True, min_length=1)
    url: AnyHttpUrl
    # the pattern for posts' url is like this: https://fastblog.io/@username/slugged-title-somehash
    # this is generated automatically for posts that'll be published


class TokenSchema(BaseModel):
    access_token: str
    token_type: str


class UserSignUpSchema(BaseModel):
    username: str
    password: constr(strip_whitespace=True, min_length=8)


class UserLoginSchema(UserSignUpSchema):
    pass


class UserOutSchema(BaseModel):
    username: str
    created: datetime
    posts: list[PostSchema]


class UserInternalSchema(UserOutSchema):
    id: UUID


class UserInDBSchema(UserInternalSchema):
    password: str
