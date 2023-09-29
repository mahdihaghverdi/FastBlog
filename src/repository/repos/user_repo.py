from sqlalchemy import select, insert
from sqlalchemy.exc import IntegrityError

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

    async def get(self, self_id):
        stmt = select(UserModel).where(UserModel.id == self_id)
        user = (await self.session.execute(stmt)).scalar_one_or_none()
        if user is not None:
            return User(**user.sync_dict(), model=user)

    async def get_by_username(self, username) -> User | None:
        stmt = select(UserModel).where(UserModel.username == username)
        user = (await self.session.execute(stmt)).scalar_one_or_none()
        if user is not None:
            return User(**user.sync_dict(), model=user)

    async def add(self, data: dict) -> User:
        password = hash_password(data["password"])
        stmt = (
            insert(UserModel)
            .values(username=data["username"], password=password)
            .returning(UserModel)
        )

        try:
            user = (await self.session.execute(stmt)).scalar_one_or_none()
        except IntegrityError:
            raise DuplicateUsernameError(
                f"username: {data['username']!r} already exists!",
            )
        return User(**user.sync_dict(), model=user)
