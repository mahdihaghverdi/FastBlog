from datetime import datetime
from typing import Protocol

from sqlalchemy import select, insert
from sqlalchemy.exc import IntegrityError
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

    async def get(self, self_id):
        record = await self.session.get(self.model, self_id)
        if record is not None:
            return record

    async def add(self, data: dict):
        stmt = insert(self.model).values(**data).returning(self.model)
        try:
            user = (await self.session.execute(stmt)).scalar_one_or_none()
        except IntegrityError:
            return None
        return user.sync_dict()


class OneToManyRelRepoMixin:
    """Provide the shared functionality for models

    This mixin's methods do the core operation like:
      - get the record from database
      - add a record to database
      - update the record
      - delete a record

    if you want to override, please do the needed work and
    let this parent class do the core functionality
    """

    async def _get(self, username, self_id):
        stmt = (
            select(self.model)
            .where(self.model.username == username)
            .where(self.model.id == self_id)
        )
        record = (await self.session.execute(stmt)).scalar_one_or_none()
        if record is not None:
            return record

    async def get(self, username, self_id):
        record = await self._get(username, self_id)
        if record is not None:
            return record.sync_dict()

    async def add(self, username, data: dict):
        """Inserts the model with the provided data and returns it"""
        stmt = (
            insert(self.model).values(**data, username=username).returning(self.model)
        )
        record = (await self.session.execute(stmt)).scalar_one_or_none()
        return record

    async def update(self, username, /, self_id, data: dict):
        record = await self._get(username, self_id)
        if record is None:
            return

        data = {k: v for k, v in data.items() if v is not None}
        for key, value in data.items():
            setattr(record, key, value)
        setattr(record, "updated", datetime.utcnow())
        return record

    async def delete(self, username, /, self_id):
        record = await self._get(username, self_id)
        if record is None:
            return False
        await self.session.delete(record)
