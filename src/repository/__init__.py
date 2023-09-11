from abc import ABC
from typing import Protocol
from uuid import UUID

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


class BaseRepo(ABC, RepoProtocol):
    def __init__(
        self,
        session: AsyncSession,
        model: type[Base],
        object_: type[BusinessObject],
    ):
        self.model = model
        self.object = object_
        self.session = session

    async def get(self, self_id: UUID):
        record = await self.session.get(self.model, self_id)
        if record is not None:
            return self.object(**(await record.dict()), model=record)


class RelatedObjectsRepoMixin(ABC, RepoProtocol):
    async def _get_related(self, user_id: UUID, self_id: UUID) -> type[Base] | None:
        stmt = (
            select(self.model)
            .where(self.model.user_id == user_id)
            .where(self.model.id == self_id)
        )
        record = (await self.session.execute(stmt)).first()
        if record is not None:
            return record[0]

    async def add(self, user_id, data: dict):
        record = self.model(**data, user_id=user_id)
        self.session.add(record)
        return self.object(**(await record.dict()), model=record)

    async def get(self, user_id, /, self_id):
        record = await self._get_related(user_id, self_id)
        if record is not None:
            return self.object(**(await record.dict()), model=record)

    async def update(self, user_id, /, self_id, data: dict):
        record = await self._get_related(user_id, self_id)
        if record is None:
            return
        for key, value in data.items():
            setattr(record, key, value)
        return self.object(**(await record.dict()), model=record)

    async def delete(self, user_id: UUID, /, self_id):
        record = await self._get_related(user_id, self_id)
        if record is None:
            return False
        await self.session.delete(record)
