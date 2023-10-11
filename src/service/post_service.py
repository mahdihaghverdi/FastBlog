from src.common.exceptions import PostNotFoundError
from src.service import Service
from src.service.objects import Post
from src.web.core.schemas import Sort


async def slugify(post, user):
    slug = post.slug(user.username)
    post_dict = post.model_dump()
    del post_dict["title_in_url"]
    post_dict["url"] = slug
    return post_dict


class PostService(Service):
    async def list_posts(
        self,
        user,
        *,
        page: int,
        per_page: int,
        sort: Sort,
        desc_: bool,
    ) -> list[Post]:
        return await self.repo.list(
            user.username,
            page=page,
            per_page=per_page,
            sort=sort,
            desc_=desc_,
        )

    async def create_post(self, user, post):
        post_dict = await slugify(post, user)
        return await self.repo.add(user.username, post_dict)

    async def get_post(self, user, post_id):
        post = await self.repo.get(user.username, post_id)
        if post is None:
            raise PostNotFoundError(f"post with id: '{post_id}' is not found")
        return post

    async def update_post(self, user, post_id, post):
        post_dict = await slugify(post, user)
        post = await self.repo.update(user.username, post_id, post_dict)
        if post is None:
            raise PostNotFoundError(f"post with id: '{post_id}' is not found")
        return post

    # TODO: write tests for PostNotFoundError
    async def delete_post(self, user, post_id):
        deleted = await self.repo.delete(user.username, post_id)
        if deleted is False:
            raise PostNotFoundError(f"post with id: '{post_id}' is not found")

    async def get_post_by_post_url(self, username, post_slug):
        user = await self.user_repo.get_by_username(username)
        if user is None:
            raise PostNotFoundError(f"post: @{username}/{post_slug} is not found!")

        post = await self.repo.get_post_with_url(
            username=user["username"],
            url=f"/@{username}/{post_slug}",
        )

        if post is None:
            raise PostNotFoundError(f"post: @{username}/{post_slug} is not found!")

        return post

    # TODO: do post existence first
    async def add_comment(self, user, post_id, comment):
        # self.repo = None, self.comment_repo is available
        return await self.comment_repo.add(
            user.username,
            post_id,
            parent_id=None,
            comment=comment,
        )
