from abc import ABC, abstractmethod


class BaseBusinessObject(ABC):
    @abstractmethod
    async def dict(self):
        raise NotImplementedError


class Post(BaseBusinessObject):
    def __init__(self, *, id, created, title, body, post_model=None):
        self.id = id
        self.created = created
        self.title = title
        self.body = body
        self.post_model = post_model

    async def dict(self):
        return {
            "id": self.id or (await self.post_model.dict())["id"],
            "created": self.created or (await self.post_model.dict())["created"],
            "title": self.title,
            "body": self.body,
        }
