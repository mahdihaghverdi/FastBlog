from abc import ABC, abstractmethod
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.models import Base
from src.service.posts import BaseBusinessObject


class BaseRepo(ABC):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _get(self, model: type[Base], id_: UUID) -> type[Base] | None:
        return await self.session.get(model, id_)

    async def _get_related(self, model, user_id, self_id) -> tuple[type[Base]] | None:
        stmt = select(model).where(model.user_id == user_id).where(model.id == self_id)
        return (await self.session.execute(stmt)).first()

    @abstractmethod
    async def get(self, id_: UUID) -> BaseBusinessObject | None:
        raise NotImplementedError

    @abstractmethod
    async def add(self, data: dict) -> BaseBusinessObject:
        raise NotImplementedError

    @abstractmethod
    async def update(self, id_: UUID, data: dict) -> BaseBusinessObject | None:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, id_: UUID) -> BaseBusinessObject | None:
        raise NotImplementedError

    @abstractmethod
    async def list(self, **kwargs) -> list[BaseBusinessObject]:
        raise NotImplementedError
