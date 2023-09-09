class ResourceNotFoundError(Exception):
    pass


class PostNotFoundError(ResourceNotFoundError):
    pass


class UserNotFoundError(ResourceNotFoundError):
    pass


class DuplicateUsernameError(Exception):
    pass


class UnAuthorizedError(Exception):
    pass


class UnAuthorizedLoginError(UnAuthorizedError):
    pass
