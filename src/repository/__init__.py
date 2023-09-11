from abc import ABC
from typing import Protocol
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.models import Base
from src.service.objects import BaseBusinessObject


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
        object_: type[BaseBusinessObject],
    ):
        self.model = model
        self.object = object_
        self.session = session

    async def _get(self, self_id: UUID) -> type[Base] | None:
        return await self.session.get(self.model, self_id)


class RelatedObjectsRepoMixin(ABC, RepoProtocol):
    async def _get_related(
        self,
        model: type[Base],
        user_id: UUID,
        self_id: UUID,
    ) -> type[Base] | None:
        stmt = select(model).where(model.user_id == user_id).where(model.id == self_id)
        record = (await self.session.execute(stmt)).first()
        if record is not None:
            return record[0]
