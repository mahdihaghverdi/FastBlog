import itertools

from sqlalchemy import desc, select

from src.repository.repos import BaseRepo, OneToManyRelRepo
from src.repository.models import PostModel
from src.repository.repos.tag_repo import TagRepo
from src.service.objects import Post
from src.web.core.schemas import Sort


class PostRepo(OneToManyRelRepo, BaseRepo):
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

        return self.object(**(await record.dict()), model=record)

    async def update(self, user_id, post_id, data: dict):
        record = await self._get_related(user_id, post_id)
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
        return Post(**(await record.dict()), model=record)

    async def list(
        self,
        user_id,
        *,
        page: int,
        per_page: int,
        sort: Sort,
        desc_: bool,
    ) -> list[Post]:
        """Return a list of Post objects

        This function paginates the results according to page and per_page
        This function sorts the results according to `Sort` and `SortOrder` values
        """
        order_by_column = PostModel.title if sort is Sort.TITLE else PostModel.created
        stmt = (
            select(PostModel)
            .where(PostModel.user_id == user_id)
            .offset((page - 1) * per_page)
            .limit(per_page)
            .order_by(
                desc(order_by_column) if desc_ else order_by_column,
            )
        )
        records = list(
            itertools.chain.from_iterable((await self.session.execute(stmt)).all()),
        )
        return [Post(**(await record.dict()), model=record) for record in records]

    async def filter_get(self, **filters):
        stmt = select(PostModel).filter_by(**filters)
        post = (await self.session.execute(stmt)).first()[0]
        if post is not None:
            return Post(**(await post.dict()), model=post)
