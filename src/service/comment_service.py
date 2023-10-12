from src.common.exceptions import CommentNotFoundError, PostNotFoundError
from src.service import Service


# TODO: decorate all methods to check post existence
class CommentService(Service):
    async def reply(self, user, post_id, comment_id, reply):
        if not await self.post_repo.exists(post_id):
            raise PostNotFoundError(f"Post with id: '{post_id}' is not found")
        return await self.repo.add(
            user.username,
            {"post_id": post_id, "parent_id": comment_id, "comment": reply},
        )

    async def get_comments(self, post_id, comment_id, reply_level):
        if not await self.post_repo.exists(post_id):
            raise PostNotFoundError(f"Post with id: '{post_id}' is not found")
        return await self.repo.list(post_id, comment_id, reply_level)

    async def update_comment(self, user, post_id, comment_id, comment):
        if not await self.post_repo.exists(post_id):
            raise PostNotFoundError(f"Post with id: '{post_id}' is not found")
        comment = await self.repo.update(
            user.username,
            comment_id,
            {"comment": comment},
        )
        if comment is None:
            raise CommentNotFoundError(f"Comment with id: '{comment}' not found")
        return comment

    async def delete_comment(self, user, post_id, comment_id):
        if not await self.post_repo.exists(post_id):
            raise PostNotFoundError(f"Post with id: '{post_id}' is not found")
        result = await self.repo.delete(user.username, comment_id)
        if result is False:
            raise CommentNotFoundError(f"Comment with id: '{comment_id}' is not found")
