class ResourceNotFoundError(Exception):
    def __init__(self, not_found):
        self.not_found = not_found

    def __str__(self):
        return f"<{self.kind.upper()}:{self.not_found!r}> is not found!"


class PostNotFoundError(ResourceNotFoundError):
    kind = "post"


class CommentNotFoundError(ResourceNotFoundError):
    kind = "comment"


class DraftNotFoundError(ResourceNotFoundError):
    kind = "draft"


class UserNotFoundError(ResourceNotFoundError):
    kind = "user"


class DuplicateUsernameError(Exception):
    pass


class UnAuthorizedError(Exception):
    pass


class UnAuthorizedLoginError(UnAuthorizedError):
    pass
