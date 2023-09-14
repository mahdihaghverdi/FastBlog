from datetime import datetime

from pydantic import BaseModel, constr, AnyHttpUrl, conlist

from src.web.core.schemas.tag import TagSchema


class CreatePostSchema(BaseModel):
    title: constr(strip_whitespace=True, min_length=1)
    body: constr(strip_whitespace=True, min_length=1)
    tags: conlist(TagSchema, min_length=1, max_length=5, unique_items=True)
    title_in_url: constr(strip_whitespace=True, min_length=1) | None = None


class PostSchema(BaseModel):
    id: int
    created: datetime
    title: constr(strip_whitespace=True, min_length=1)
    body: constr(strip_whitespace=True, min_length=1)
    url: AnyHttpUrl
    # the pattern for posts' url is like this: https://fastblog.io/@username/slugged-title-somehash
    # this is generated automatically for posts that'll be published
    tags: list[TagSchema]
