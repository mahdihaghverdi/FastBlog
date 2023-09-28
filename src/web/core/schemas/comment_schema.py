from datetime import datetime

from pydantic import BaseModel


class CommentSchema(BaseModel):
    id: int
    created: datetime
    comment: str
    parent_id: int | None
    path: str | None
    username: str
    reply_count: int
