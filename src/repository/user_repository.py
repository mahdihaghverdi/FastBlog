from uuid import UUID


from src.repository import BaseRepo
from src.repository.models import UserModel
from src.service.posts import BaseBusinessObject
from src.service.users import User
from src.web.core.security import hash_password


class UserRepo(BaseRepo):
    async def get(self, id_: UUID) -> BaseBusinessObject | None:
        user = await self._get(UserModel, id_)
        if user is not None:
            return User(**(await user.dict()))

    async def add(self, data: dict) -> BaseBusinessObject:
        data = data.copy()
        data["password"] = hash_password(data["password"])
        record = UserModel(**data)
        self.session.add(record)
        return User(**(await record.dict()), user_model=record)

    async def update(self, id_: UUID, data: dict) -> BaseBusinessObject | None:
        pass

    async def delete(self, id_: UUID) -> BaseBusinessObject | None:
        pass

    async def list(self, **kwargs) -> list[BaseBusinessObject]:
        pass
