class Post:
    def __init__(self, *, id, created, title, body, post_model=None):
        self.id = id
        self.created = created
        self.title = title
        self.body = body
        self.post_model = post_model

    async def dict(self):
        return {
            "id": self.id or (await self.post_model.awaitable_attrs.id),
            "created": self.created or (await self.post_model.awaitable_attrs.created),
            "title": self.title,
            "body": self.body,
        }
