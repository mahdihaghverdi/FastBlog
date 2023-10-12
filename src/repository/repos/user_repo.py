from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select, func, inspect

from src.repository.models import UserModel, PostModel, DraftModel
from src.repository.repos import BaseRepo
from src.service.objects import User
from src.web.core.security import hash_password


@dataclass
class _Post:
    title: str
    url: str
    created: datetime

    def __bool__(self):
        return all([self.title, self.url, self.created])


@dataclass
class _Draft:
    title: str
    created: datetime

    def __bool__(self):
        return all([self.title, self.created])


class UserRepo(BaseRepo[UserModel]):
    def __init__(self, session):
        super().__init__(session=session, model=UserModel)

    async def get(self, self_id, raw=False) -> UserModel | User:
        if raw:
            return await super().get(self_id)
        return User(**(await super().get(self_id)).sync_dict())

    async def get_full(self, self_id):
        stmt = (
            select(
                inspect(self.model).columns,
                func.array_agg(PostModel.title).label("post_title"),
                func.array_agg(PostModel.url).label("post_url"),
                func.array_agg(PostModel.created).label("post_created"),
                func.array_agg(DraftModel.title).label("draft_title"),
                func.array_agg(DraftModel.created).label("draft_created"),
            )
            .outerjoin(PostModel, PostModel.username == self.model.username)
            .outerjoin(DraftModel, DraftModel.username == self.model.username)
            .filter(self.model.id == self_id)
            .group_by(self.model)
        )
        user = dict((await self.session.execute(stmt)).mappings().one_or_none())

        _post_titles = user.pop("post_title")
        _post_urls = user.pop("post_url")
        _post_createds = user.pop("post_created")

        _draft_titles = user.pop("draft_title")
        _draft_createds = user.pop("draft_created")

        user.update(
            {
                "posts": list(
                    filter(
                        bool,
                        (
                            _Post(*post)
                            for post in zip(_post_titles, _post_urls, _post_createds)
                        ),
                    ),
                ),
            },
        )
        user.update(
            {
                "drafts": list(
                    filter(
                        bool,
                        (
                            _Draft(*draft)
                            for draft in zip(_draft_titles, _draft_createds)
                        ),
                    ),
                ),
            },
        )
        return user

    async def get_by_username(self, username) -> dict | None:
        stmt = select(self.model).where(self.model.username == username)
        user = (await self.session.execute(stmt)).scalar_one_or_none()
        if user is not None:
            return user.sync_dict()

    async def add(self, data) -> User | None:
        password = hash_password(data["password"])
        data["password"] = password
        user = await super().add(data)
        if user is None:
            return None
        return User(**user.sync_dict())
