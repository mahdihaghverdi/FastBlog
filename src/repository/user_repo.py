from uuid import UUID

from sqlalchemy import select

from src.repository import BaseRepo
from src.repository.models import UserModel
from src.service.objects.users import User
from src.web.core.security import hash_password


class UserRepo(BaseRepo):
    def __init__(self, session):
        model = UserModel
        object_ = User
        super().__init__(session, model, object_)

    async def get(self, id_: UUID) -> User | None:
        user = await self._get(id_)
        if user is not None:
            return User(**(await user.dict()))

    async def get_by_username(self, username) -> User | None:
        stmt = select(UserModel).where(UserModel.username == username)
        user = (await self.session.execute(stmt)).first()
        if user is not None:
            return User(**(await user[0].dict()))

    async def add(self, data: dict) -> User:
        data = data.copy()
        data["password"] = hash_password(data["password"])
        record = UserModel(**data)
        self.session.add(record)
        return User(**(await record.dict()), user_model=record)

    async def update(self, id_: UUID, data: dict) -> User | None:
        pass

    async def delete(self, id_: UUID) -> User | None:
        pass

    async def list(self, **kwargs) -> list[User]:
        pass
