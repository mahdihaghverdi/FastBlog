import functools
import inspect

from src.common.exceptions import CommentNotFoundError, PostNotFoundError
from src.service import Service


def _check_post_existence_decorator(async_method):
    @functools.wraps(async_method)
    async def decorator(self, **kwargs):
        post_id = kwargs["post_id"]
        if not await self.post_repo.exists(post_id):
            raise PostNotFoundError(post_id)
        return await async_method(self, **kwargs)

    return decorator


def check_post_existence(decorator):
    def decorate(cls):
        for name, fn in [
            i
            for i in inspect.getmembers(cls, inspect.isroutine)
            if not i[0].startswith("__")
        ]:
            setattr(cls, name, decorator(fn))
        return cls

    return decorate


@check_post_existence(_check_post_existence_decorator)
class CommentService(Service):
    async def reply(self, *, username, post_id, comment_id, reply):
        reply = await self.repo.add(
            username,
            {"post_id": post_id, "parent_id": comment_id, "comment": reply},
        )
        if reply is None:
            raise CommentNotFoundError(comment_id)
        return reply

    async def get_comments(self, *, post_id, comment_id, reply_level):
        return await self.repo.list(post_id, comment_id, reply_level)

    async def update_comment(self, *, username, post_id, comment_id, comment):
        comment = await self.repo.update(
            username,
            comment_id,
            {"comment": comment},
        )
        if comment is None:
            raise CommentNotFoundError(comment_id)
        return comment

    async def delete_comment(self, *, username, post_id, comment_id):
        result = await self.repo.delete(username, comment_id)
        if result is False:
            raise CommentNotFoundError(comment_id)
