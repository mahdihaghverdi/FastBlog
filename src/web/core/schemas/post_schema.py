from datetime import datetime

from pydantic import BaseModel, constr, AnyHttpUrl, conset, model_serializer
from slugify import Slugify

from src.common.utils import generate_hash


class CreatePostSchema(BaseModel):
    title: constr(strip_whitespace=True, min_length=1)
    body: constr(strip_whitespace=True, min_length=1)
    tags: conset(
        constr(strip_whitespace=True, to_lower=True, min_length=1),
        min_length=1,
        max_length=5,
    )
    title_in_url: constr(strip_whitespace=True, min_length=1) | None = None

    def slug(self, username):
        slugify = Slugify(to_lower=True)

        if self.title_in_url is None:
            slug = slugify(f"{self.title} {generate_hash()}")
        else:
            slug = slugify(f"{self.title_in_url} {generate_hash()}")
        return f"/@{username}/{slug}"


class UpdatePostSchema(BaseModel):
    title: constr(strip_whitespace=True, min_length=1) | None = None
    body: constr(strip_whitespace=True, min_length=1) | None = None
    tags: conset(
        constr(strip_whitespace=True, to_lower=True, min_length=1),
        min_length=1,
        max_length=5,
    ) | None = None
    title_in_url: constr(strip_whitespace=True, min_length=1) | None = None

    def slug(self, username):
        slugify = Slugify(to_lower=True)

        if self.title_in_url is not None:
            slug = slugify(f"{self.title_in_url} {generate_hash()}")
            return f"/@{username}/{slug}"


class TagSchema(BaseModel):
    name: str

    @model_serializer
    def ser_model(self) -> str:
        return self.name


class PostSchema(BaseModel):
    id: int
    created: datetime
    updated: datetime | None = None
    title: constr(strip_whitespace=True, min_length=1)
    body: constr(strip_whitespace=True, min_length=1)
    username: str

    # the pattern for posts' url is like this: https://fastblog.io/@username/slugged-title-somehash
    # this is generated automatically for posts that'll be published
    url: AnyHttpUrl
    tags: list[str]


class GlobalPostSchema(PostSchema):
    all_comments_count: int
    base_comments_count: int
    reply_comments_count: int
