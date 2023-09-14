from datetime import datetime
from uuid import UUID

from slugify import Slugify

from src.common.exceptions import PostNotFoundError
from src.repository.repos.user_repo import UserRepo
from src.service import Service
from src.service.objects import Post
from src.web.core.schemas import Sort


class PostService(Service):
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
        slugify = Slugify(to_lower=True)

        pre_title_in_url = post.pop("title_in_url")
        if pre_title_in_url is None:
            title_slug = slugify(f"{post['title']} {hex(hash(datetime.utcnow()))}")
        else:
            title_slug = slugify(f"{pre_title_in_url} {hex(hash(datetime.utcnow()))}")

        username = (await UserRepo(self.repo.session).get(user_id)).username
        post["url"] = f"/@{username}/{title_slug}"
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

    async def get_post_by_post_url(self, username, post_slug):
        user_id = (await UserRepo(self.repo.session).get_by_username(username)).id
        post = await self.repo.filter_get(
            user_id=user_id,
            url=f"/@{username}/{post_slug}",
        )
        if post is None:
            raise PostNotFoundError(f"post: @{username}/{post_slug} is not found!")
        return post
