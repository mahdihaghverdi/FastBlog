from datetime import datetime

from pydantic import BaseModel


class CommentSchema(BaseModel):
    id: int
    created: datetime
    post_id: int
    parent_id: int | None
    comment: str


class CommentOnGlobalPost(BaseModel):
    id: int
    created: datetime
    parent_id: int
    comment: str
