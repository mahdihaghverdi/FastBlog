from datetime import datetime

from pydantic import BaseModel, constr, AnyHttpUrl
from slugify import Slugify


class CreatePostSchema(BaseModel):
    title: constr(strip_whitespace=True, min_length=1)
    body: constr(strip_whitespace=True, min_length=1)
    # tags: conlist(TagSchema, min_length=1, max_length=5, unique_items=True)
    title_in_url: constr(strip_whitespace=True, min_length=1) | None = None

    def slug(self, username):
        slugify = Slugify(to_lower=True)

        if self.title_in_url is None:
            slug = slugify(f"{self.title} {hex(hash(datetime.utcnow()))}")
        else:
            slug = slugify(f"{self.title_in_url} {hex(hash(datetime.utcnow()))}")
        return f"/@{username}/{slug}"


class PostSchema(BaseModel):
    id: int
    created: datetime
    title: constr(strip_whitespace=True, min_length=1)
    body: constr(strip_whitespace=True, min_length=1)
    url: AnyHttpUrl
    # the pattern for posts' url is like this: https://fastblog.io/@username/slugged-title-somehash
    # this is generated automatically for posts that'll be published
    # tags: list[TagSchema]
