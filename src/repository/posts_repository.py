import itertools

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.models import PostModel
from src.service.posts import Post
from src.web.api.schemas import Sort


class PostsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

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
        return [Post(**record.dict()) for record in records]

    async def add(self, post: dict):
        record = PostModel(**post)
        self.session.add(record)
        return Post(**record.dict(), post_model=record)
