from sqlalchemy import select

from src.common.exceptions import DuplicateUsernameError
from src.repository.repos import BaseRepo
from src.repository.models import UserModel
from src.service.objects import User
from src.web.core.security import hash_password


class UserRepo(BaseRepo):
    def __init__(self, session):
        model = UserModel
        object_ = User
        super().__init__(session=session, model=model, object_=object_)

    async def get(self, self_id, raw=False):
        if raw:
            return await super().get(self_id)
        return User(**(await super().get(self_id)).sync_dict())

    async def get_by_username(self, username):
        stmt = select(UserModel).where(UserModel.username == username)
        user = (await self.session.execute(stmt)).scalar_one_or_none()
        if user is not None:
            return user.sync_dict()

    async def add(self, data):
        password = hash_password(data["password"])
        data["password"] = password
        user = await super().add(data)
        if user is None:
            raise DuplicateUsernameError(
                f"username: {data['username']!r} already exists!",
            )
        return User(**user)
