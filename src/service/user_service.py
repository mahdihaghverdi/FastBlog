from src.common.exceptions import UserNotFoundError
from src.service.users import User


class UserService:
    def __init__(self, user_repository):
        self.user_repository = user_repository

    async def get_user(self, user_id) -> User:
        user = await self.user_repository.get(user_id)
        if user is None:
            raise UserNotFoundError(f"user with id: {user_id} is not found!")
        return user
