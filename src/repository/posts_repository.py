import itertools
from uuid import UUID

from sqlalchemy import desc, select

from src.repository import BaseRepository
from src.repository.models import PostModel
from src.service.posts import Post
from src.web.api.schemas import Sort


class PostsRepository(BaseRepository):
    async def list(
        self,
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
            .offset((page - 1) * per_page)
            .limit(per_page)
            .order_by(
                desc(order_by_column) if desc_ else order_by_column,
            )
        )
        records = list(
            itertools.chain.from_iterable((await self.session.execute(stmt)).all()),
        )
        return [Post(**(await record.dict())) for record in records]

    async def add(self, post: dict) -> Post:
        record = PostModel(**post)
        self.session.add(record)
        return Post(**(await record.dict()), post_model=record)

    async def get(self, post_id: UUID) -> Post | None:
        post = await self._get(PostModel, post_id)
        if post is not None:
            return Post(**(await post.dict()))

    async def update(self, post_id: UUID, post_detail: dict) -> Post | None:
        post = await self._get(PostModel, post_id)
        if post is None:
            return
        for key, value in post_detail.items():
            setattr(post, key, value)
        return Post(**(await post.dict()), post_model=post)

    async def delete(self, post_id: UUID) -> bool | None:
        post = await self._get(PostModel, post_id)
        if post is None:
            return False
        await self.session.delete(post)
