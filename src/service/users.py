from src.service import BaseBusinessObject


class User(BaseBusinessObject):
    def __init__(self, *, id, username, password, posts, user_model=None):
        self.id = id
        self.username = username
        self.password = password
        self.posts = posts
        self.user_model = user_model

    async def dict(self):
        return {
            "id": self.id or (await self.user_model.dict())["id"],
            "username": self.username,
            "password": self.password,
            "posts": self.posts or (await self.user_model.dict())["posts"],
        }
