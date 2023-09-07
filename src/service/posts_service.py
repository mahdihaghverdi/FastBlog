from uuid import UUID

from src.service.posts import Post
from src.web.api.schemas import Sort
from src.common.exceptions import PostNotFoundError


class PostsService:
    def __init__(self, posts_repository):
        self.posts_repository = posts_repository

    async def list_posts(
        self,
        *,
        page: int,
        per_page: int,
        sort: Sort,
        desc_: bool,
    ) -> list[Post]:
        return await self.posts_repository.list(
            page=page,
            per_page=per_page,
            sort=sort,
            desc_=desc_,
        )

    async def create_post(self, post: dict) -> Post:
        return await self.posts_repository.add(post)

    async def get_post(self, post_id) -> Post:
        post = await self.posts_repository.get(post_id)
        if post is None:
            raise PostNotFoundError(f"post with id: '{post_id}' is not found")
        return post

    async def update_post(self, post_id: UUID, post_detail: dict):
        post = await self.posts_repository.update(post_id, post_detail)
        if post is None:
            raise PostNotFoundError(f"post with id: '{post_id}' is not found")
        return post

    async def delete_post(self, post_id):
        deleted = await self.posts_repository.delete(post_id)
        if deleted is False:
            raise PostNotFoundError(f"post with id: '{post_id}' is not found")
