class ResourceNotFoundError(Exception):
    pass


class PostNotFoundError(ResourceNotFoundError):
    pass


class UserNotFoundError(ResourceNotFoundError):
    pass
