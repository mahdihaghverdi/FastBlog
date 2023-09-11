from src.service import Service


class DraftPostService(Service):
    async def create_draft_post(self, user_id, post: dict):
        return await self.repo.add(user_id, post)
