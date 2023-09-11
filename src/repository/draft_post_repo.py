from src.repository import BaseRepo, RelatedObjectsRepoMixin


class DraftPostRepo(RelatedObjectsRepoMixin, BaseRepo):
    async def add(self, *args, **kwargs):
        pass
