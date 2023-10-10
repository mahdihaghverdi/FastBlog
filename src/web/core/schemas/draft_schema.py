from datetime import datetime

from pydantic import BaseModel, constr, conset
from slugify import Slugify

from src.common.utils import generate_hash


class CreateDraftSchema(BaseModel):
    title: constr(strip_whitespace=True, min_length=1)
    body: constr(strip_whitespace=True, min_length=1)


class DraftSchema(BaseModel):
    id: int
    created: datetime
    updated: datetime | None = None
    title: constr(strip_whitespace=True, min_length=1)
    body: constr(strip_whitespace=True, min_length=1)


class PublishSchema(BaseModel):
    title_in_url: constr(strip_whitespace=True, min_length=1) | None = None
    tags: conset(
        constr(strip_whitespace=True, to_lower=True, min_length=1),
        min_length=1,
        max_length=5,
    )

    def slug(self, title, username):
        slugify = Slugify(to_lower=True)

        if self.title_in_url is None:
            slug = slugify(f"{title} {generate_hash()}")
        else:
            slug = slugify(f"{self.title_in_url} {generate_hash()}")
        return f"/@{username}/{slug}"
