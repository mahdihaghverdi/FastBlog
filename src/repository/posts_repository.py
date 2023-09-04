from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.models import PostModel
from src.service.posts import Post
from src.web.api.schemas import SortOrder, Sort


class PostsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(
        self,
        *,
        page: int,
        per_page: int,
        sort: Sort,
        order: SortOrder,
    ) -> list[Post]:
        """Return a list of Post objects

        This function paginates the results according to page and per_page
        This function sorts the results according to `Sort` and `SortOrder` values
        """
        stmt = select(PostModel).offset((page - 1) * per_page).limit(per_page)
        match (sort, order):
            case (Sort.NAME, SortOrder.ASC):
                stmt = stmt.order_by(PostModel.title)
            case (Sort.DATE, SortOrder.ASC):
                stmt = stmt.order_by(PostModel.created)
            case (Sort.NAME, SortOrder.DESC):
                stmt = stmt.order_by(desc(PostModel.title))
            case (Sort.DATE, SortOrder.DESC):
                stmt = stmt.order_by(desc(PostModel.created))
        records = await self.session.execute(stmt)
        return [Post(**record.dict()) for record in records]

    async def add(self, post: dict):
        record = PostModel(**post)
        self.session.add(record)
        return Post(**record.dict(), post_model=record)
