from datetime import datetime

from pydantic import BaseModel, constr


class CreateDraftSchema(BaseModel):
    title: constr(strip_whitespace=True, min_length=1)
    body: constr(strip_whitespace=True, min_length=1)


class DraftSchema(BaseModel):
    id: int
    created: datetime
    title: constr(strip_whitespace=True, min_length=1)
    body: constr(strip_whitespace=True, min_length=1)
