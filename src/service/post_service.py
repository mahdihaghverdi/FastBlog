from uuid import UUID

from src.common.exceptions import PostNotFoundError
from src.service import BaseService
from src.service.objects.posts import Post
from src.web.core.schemas import Sort


class PostService(BaseService):
    async def list_posts(
        self,
        user_id,
        *,
        page: int,
        per_page: int,
        sort: Sort,
        desc_: bool,
    ) -> list[Post]:
        return await self.repo.list(
            user_id,
            page=page,
            per_page=per_page,
            sort=sort,
            desc_=desc_,
        )

    async def create_post(self, user_id, post: dict) -> Post:
        return await self.repo.add(user_id, post)

    async def get_post(self, user_id, post_id) -> Post:
        post = await self.repo.get(user_id, post_id)
        if post is None:
            raise PostNotFoundError(f"post with id: '{post_id}' is not found")
        return post

    async def update_post(self, user_id, post_id: UUID, post_detail: dict):
        post = await self.repo.update(user_id, post_id, post_detail)
        if post is None:
            raise PostNotFoundError(f"post with id: '{post_id}' is not found")
        return post

    async def delete_post(self, user_id, post_id):
        deleted = await self.repo.delete(user_id, post_id)
        if deleted is False:
            raise PostNotFoundError(f"post with id: '{post_id}' is not found")
