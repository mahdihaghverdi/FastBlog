from datetime import datetime

from pydantic import BaseModel


class CommentSchema(BaseModel):
    id: int
    created: datetime
    comment: str
    parent_id: int | None
    path: str | None
    post_id: int
    user_id: int
    username: str


class CommentOnGlobalPost(BaseModel):
    id: int
    created: datetime
    parent_id: int
    comment: str
