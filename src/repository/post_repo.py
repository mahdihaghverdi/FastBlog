import itertools

from sqlalchemy import desc, select

from src.repository import BaseRepo, RelatedObjectsRepoMixin
from src.repository.models import PostModel
from src.service.objects import Post
from src.web.core.schemas import Sort


class PostRepo(RelatedObjectsRepoMixin, BaseRepo):
    def __init__(self, session):
        model = PostModel
        object_ = Post
        super().__init__(session, model, object_)

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
