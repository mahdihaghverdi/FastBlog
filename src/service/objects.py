class BusinessObject:
    def __init__(self, model=None, **kwargs):
        self.model = model
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __repr__(self):
        attrs = ", ".join(
            f"{key}={value!r}" if key != "model" else f"{value.__class__.__name__!r}"
            for key, value in self.__dict__.items()
        )
        return f"<{self.__class__.__name__}: {attrs}>"

    def sync_dict(self):
        return self.model.sync_dict()


class Post(BusinessObject):
    pass


class User(BusinessObject):
    pass


class Draft(BusinessObject):
    pass


class Tag(BusinessObject):
    pass


class Comment(BusinessObject):
    pass
