from src.common.exceptions import UserNotFoundError, UnAuthorizedLoginError
from src.service import Service
from src.web.core.security import verify_password


class UserService(Service):
    async def get_user(self, user_id):
        user = await self.repo.get(user_id)
        if user is None:
            raise UserNotFoundError(f"user with id: {user_id} is not found!")
        return user

    async def create_user(self, user_data: dict):
        return await self.repo.add(user_data)

    async def authenticate(self, user_data: dict):
        username, password = user_data["username"], user_data["password"]
        user = await self.repo.get_by_username(username)
        if user is None:
            raise UnAuthorizedLoginError()
        verify = verify_password(password, user["password"])
        if not verify:
            raise UnAuthorizedLoginError()
        return user
