import itertools
from typing import Protocol

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.models import Base
from src.service.objects import BusinessObject
from src.web.core.schemas import Sort


class RepoProtocol(Protocol):
    async def get(self, *args, **kwargs):
        ...

    async def list(self, *args, **kwargs):
        ...

    async def add(self, *args, **kwargs):
        ...

    async def update(self, *args, **kwargs):
        ...

    async def delete(self, *args, **kwargs):
        ...


class BaseRepo:
    def __init__(
        self,
        session: AsyncSession,
        model: type[Base],
        object_: type[BusinessObject],
    ):
        self.model = model
        self.object = object_
        self.session = session

    async def get(self, self_id, /, raw: bool = False):
        record = await self.session.get(self.model, self_id)
        if record is not None:
            if raw:
                return record
            return self.object(**(await record.dict()), model=record)


class OneToManyRelRepoMixin:
    async def _get(self, user_id, self_id):
        stmt = (
            select(self.model)
            .where(self.model.user_id == user_id)
            .where(self.model.id == self_id)
        )
        record = (await self.session.execute(stmt)).scalar_one_or_none()
        if record is not None:
            return record

    async def add(self, user_id, data: dict):
        record = self.model(**data, user_id=user_id)
        self.session.add(record)
        return self.object(**record.sync_dict(), model=record)

    async def get(self, user_id, self_id):
        record = await self._get(user_id, self_id)
        if record is not None:
            return self.object(**record.sync_dict(), model=record)

    async def update(self, user_id, /, self_id, data: dict):
        record = await self._get(user_id, self_id)
        if record is None:
            return
        for key, value in data.items():
            setattr(record, key, value)
        return self.object(**record.sync_dict(), model=record)

    async def delete(self, user_id, /, self_id):
        record = await self._get(user_id, self_id)
        if record is None:
            return False
        await self.session.delete(record)


class PaginationMixin:
    async def list(
        self,
        user_id,
        *,
        page: int,
        per_page: int,
        sort: Sort,
        desc_: bool,
    ) -> list:
        """Return a list of Post objects

        This function paginates the results according to page and per_page
        This function sorts the results according to `Sort` and `SortOrder` values
        """
        order_by_column = self.model.title if sort is Sort.TITLE else self.model.created
        stmt = (
            select(self.model)
            .where(self.model.user_id == user_id)
            .offset((page - 1) * per_page)
            .limit(per_page)
            .order_by(
                desc(order_by_column) if desc_ else order_by_column,
            )
        )
        records = list(
            itertools.chain.from_iterable((await self.session.execute(stmt)).all()),
        )
        return [self.object(**record.sync_dict(), model=record) for record in records]
