from datetime import datetime

from pydantic import BaseModel, constr


class UserSignUpSchema(BaseModel):
    username: str
    password: constr(strip_whitespace=True, min_length=8)


class UserLoginSchema(UserSignUpSchema):
    pass


class UserOutSchema(BaseModel):
    username: str
    created: datetime


class UserInternalSchema(UserOutSchema):
    id: int
