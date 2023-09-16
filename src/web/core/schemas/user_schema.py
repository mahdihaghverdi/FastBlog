from datetime import datetime

from pydantic import BaseModel, constr

from src.web.core.schemas import DraftSchema
from src.web.core.schemas.post_schema import PostSchema


class UserSignUpSchema(BaseModel):
    username: str
    password: constr(strip_whitespace=True, min_length=8)


class UserLoginSchema(UserSignUpSchema):
    pass


class UserOutSchema(BaseModel):
    username: str
    created: datetime
    posts: list[PostSchema]
    drafts: list[DraftSchema]


class UserInternalSchema(UserOutSchema):
    id: int
