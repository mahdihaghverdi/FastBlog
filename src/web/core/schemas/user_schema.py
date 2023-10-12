from datetime import datetime

from pydantic import BaseModel, constr, EmailStr

from src.web.core.schemas import MiniPostSchema, MiniDraftSchema


class UserSignUpSchema(BaseModel):
    name: str | None = None
    username: str
    password: constr(strip_whitespace=True, min_length=8)
    bio: str | None = None
    twitter: str | None = None
    email: EmailStr | None = None


class UserLoginSchema(BaseModel):
    username: str
    password: constr(strip_whitespace=True, min_length=8)


class UserOutSchema(UserSignUpSchema):
    created: datetime
    updated: datetime | None = None
    posts: list[MiniPostSchema]
    drafts: list[MiniDraftSchema]


class UserInternalSchema(UserOutSchema):
    id: int
