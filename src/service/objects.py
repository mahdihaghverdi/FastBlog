class BusinessObject:
    def __init__(self, model=None, **kwargs):
        self.model = model
        for key, value in kwargs.items():
            setattr(self, key, value)

    async def dict(self):
        return await self.model.dict()


class Post(BusinessObject):
    pass


class User(BusinessObject):
    pass


class DraftPost(BusinessObject):
    pass