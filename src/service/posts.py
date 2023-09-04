class Post:
    def __init__(self, *, id, created, title, body, post_model):
        self._id = id
        self._created = created
        self.title = title
        self.body = body
        self.post_model = post_model

    @property
    def id(self):
        return self._id or self.post_model.id

    @property
    def created(self):
        return self._created or self.post_model.created
