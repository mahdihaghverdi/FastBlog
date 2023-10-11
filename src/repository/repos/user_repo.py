from sqlalchemy import select

from src.common.exceptions import DuplicateUsernameError
from src.repository.models import UserModel
from src.repository.repos import BaseRepo
from src.service.objects import User
from src.web.core.security import hash_password


class UserRepo(BaseRepo[UserModel]):
    def __init__(self, session):
        super().__init__(session=session, model=UserModel)

    async def get(self, self_id, raw=False) -> UserModel | User:
        if raw:
            return await super().get(self_id)
        return User(**(await super().get(self_id)).sync_dict())

    async def get_by_username(self, username) -> dict | None:
        stmt = select(self.model).where(self.model.username == username)
        user = (await self.session.execute(stmt)).scalar_one_or_none()
        if user is not None:
            return user.sync_dict()

    async def add(self, data) -> User:
        password = hash_password(data["password"])
        data["password"] = password
        user = await super().add(data)
        if user is None:
            raise DuplicateUsernameError(
                f"username: {data['username']!r} already exists!",
            )
        return User(**user.sync_dict())
