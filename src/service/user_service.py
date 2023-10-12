from src.common.exceptions import (
    UserNotFoundError,
    UnAuthorizedLoginError,
    DuplicateUsernameError,
)
from src.service import Service
from src.web.core.security import verify_password


class UserService(Service):
    async def get_user(self, user_id, full):
        if full is False:
            user = await self.repo.get(user_id)
        else:
            user = await self.repo.get_full(user_id)
        if user is None:
            raise UserNotFoundError(user_id)
        return user

    async def create_user(self, data: dict):
        user = await self.repo.add(data)
        if user is None:
            raise DuplicateUsernameError(
                f"username: {data['username']!r} already exists!",
            )
        return user

    async def authenticate(self, user_data: dict):
        username, password = user_data["username"], user_data["password"]
        user = await self.repo.get_by_username(username)
        if user is None:
            raise UnAuthorizedLoginError()
        verify = verify_password(password, user["password"])
        if not verify:
            raise UnAuthorizedLoginError()
        return user
