from datetime import datetime

from pydantic import BaseModel, constr

from src.web.core.schemas import MiniPostSchema, MiniDraftSchema


class UserSignUpSchema(BaseModel):
    username: str
    password: constr(strip_whitespace=True, min_length=8)


class UserLoginSchema(UserSignUpSchema):
    pass


class UserOutSchema(BaseModel):
    name: str | None = None
    username: str
    bio: str | None = None
    twitter: str | None = None
    email: str | None = None
    created: datetime
    updated: datetime | None = None
    posts: list[MiniPostSchema]
    drafts: list[MiniDraftSchema]


class UserInternalSchema(UserOutSchema):
    id: int
