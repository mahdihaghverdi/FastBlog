from src.service import Service


class CommentService(Service):
    async def reply(self, user, post_id, comment_id, reply):
        return await self.repo.add(
            user.username,
            post_id,
            parent_id=comment_id,
            comment=reply,
        )

    async def get_comments(self, post_id, comment_id, reply_level):
        return await self.repo.list(post_id, comment_id, reply_level)
