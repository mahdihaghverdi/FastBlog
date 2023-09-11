from uuid import UUID

from src.repository import BaseRepo, RelatedObjectsRepoMixin


class DraftPostRepo(RelatedObjectsRepoMixin, BaseRepo):
    async def add(self, user_id: UUID, post: dict):
        pass
