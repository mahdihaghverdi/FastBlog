from sqlalchemy import select

from src.repository.models import PostModel
from src.repository.repos import BaseRepo, OneToManyRelRepoMixin, PaginationMixin
from src.repository.repos.tag_repo import TagRepo
from src.service.objects import Post


class PostRepo(PaginationMixin, OneToManyRelRepoMixin, BaseRepo):
    def __init__(self, session):
        model = PostModel
        object_ = Post
        super().__init__(session, model, object_)

    async def add(self, user_id, data: dict):
        # get or create tags
        tags = data.pop("tags")
        tags = await TagRepo(self.session).get_or_create(tags)

        record = self.model(**data, user_id=user_id)
        for tag in tags:
            record.tags.add(tag)
        self.session.add(record)
        return Post(**record.sync_dict(), model=record)

    async def update(self, user_id, post_id, data: dict):
        record = await self._get(user_id, post_id)
        if record is None:
            return

        tags = data.pop("tags")
        tags = await TagRepo(self.session).get_or_create(tags)
        record.tags.clear()
        for tag in tags:
            record.tags.add(tag)

        for key, value in data.items():
            setattr(record, key, value)
        self.session.add(record)
        return Post(**record.sync_dict(), model=record)

    async def filter_get(self, **filters):
        stmt = select(PostModel).filter_by(**filters)
        post = (await self.session.execute(stmt)).scalar_one_or_none()
        if post is not None:
            return Post(**post.sync_dict(), model=post)
