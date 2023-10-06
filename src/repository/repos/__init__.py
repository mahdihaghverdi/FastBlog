from typing import Protocol

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.models import Base
from src.service.objects import BusinessObject


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
            return self.object(**record.sync_dict(), model=record)


class OneToManyRelRepoMixin:
    async def _get(self, username, self_id):
        stmt = (
            select(self.model)
            .where(self.model.username == username)
            .where(self.model.id == self_id)
        )
        record = (await self.session.execute(stmt)).scalar_one_or_none()
        if record is not None:
            return record

    async def add(self, username, data: dict):
        record = self.model(**data, username=username)
        self.session.add(record)
        return self.object(**record.sync_dict(), model=record)

    async def get(self, username, self_id):
        record = await self._get(username, self_id)
        if record is not None:
            return record.sync_dict()

    async def update(self, username, /, self_id, data: dict):
        record = await self._get(username, self_id)
        if record is None:
            return
        for key, value in data.items():
            setattr(record, key, value)
        return self.object(**record.sync_dict(), model=record)

    async def delete(self, username, /, self_id):
        record = await self._get(username, self_id)
        if record is None:
            return False
        await self.session.delete(record)
