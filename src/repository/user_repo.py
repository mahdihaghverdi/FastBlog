from uuid import UUID

from sqlalchemy import select

from src.repository import BaseRepo
from src.repository.models import UserModel
from src.service.objects import User
from src.web.core.security import hash_password


class UserRepo(BaseRepo):
    def __init__(self, session):
        model = UserModel
        object_ = User
        super().__init__(session=session, model=model, object_=object_)

    async def get_by_username(self, username) -> User | None:
        stmt = select(UserModel).where(UserModel.username == username)
        user = (await self.session.execute(stmt)).first()
        if user is not None:
            return User(**(await user[0].dict()), model=user)

    async def add(self, data: dict) -> User:
        data = data.copy()
        data["password"] = hash_password(data["password"])
        record = UserModel(**data)
        self.session.add(record)
        return User(**(await record.dict()), model=record)

    async def update(self, id_: UUID, data: dict) -> User | None:
        pass

    async def delete(self, id_: UUID) -> User | None:
        pass

    async def list(self, **kwargs) -> list[User]:
        pass
