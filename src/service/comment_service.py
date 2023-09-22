from src.service import Service


class CommentService(Service):
    async def reply(self, user_id, post_id, comment_id, reply):
        return await self.repo.add(
            user_id,
            post_id,
            parent_id=comment_id,
            comment=reply,
        )
