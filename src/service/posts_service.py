from src.service.posts import Post
from src.web.api.schemas import Sort


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
