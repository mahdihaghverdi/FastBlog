from src.repository import BaseRepo, RelatedObjectsRepoMixin


class DraftPostRepo(RelatedObjectsRepoMixin, BaseRepo):
    async def get(self, *args, **kwargs):
        pass

    async def list(self, *args, **kwargs):
        pass

    async def add(self, *args, **kwargs):
        pass

    async def update(self, *args, **kwargs):
        pass

    async def delete(self, *args, **kwargs):
        pass
