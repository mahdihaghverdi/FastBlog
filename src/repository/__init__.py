from abc import ABC, abstractmethod
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.repository.models import Base
from src.service.posts import BaseBusinessObject


class BaseRepository(ABC):
    def __init__(self, session: AsyncSession):
        self.session = session

    async def _get(self, model: type[Base], id_: UUID) -> Base | None:
        return await self.session.get(model, id_)

    @abstractmethod
    async def get(self, id_: UUID) -> type[Base] | None:
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
