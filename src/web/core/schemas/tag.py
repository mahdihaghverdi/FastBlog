from pydantic import BaseModel, constr


class TagSchema(BaseModel):
    id: int
    name: constr(strip_whitespace=True, to_lower=True, min_length=1)
