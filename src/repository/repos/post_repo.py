from sqlalchemy import select, func, desc

from src.repository.models import (
    PostModel,
    UserModel,
    CommentModel,
    TagModel,
    association_table,
)
from src.repository.repos import BaseRepo, OneToManyRelRepoMixin
from src.repository.repos.tag_repo import TagRepo
from src.web.core.schemas import Sort


class PostRepo(OneToManyRelRepoMixin, BaseRepo[PostModel]):
    def __init__(self, session):
        super().__init__(session, PostModel)

    async def get(self, username, self_id) -> dict | None:
        post = (
            select(self.model)
            .where(self.model.id == self_id)
            .where(self.model.username == username)
        ).subquery("post")

        post_with_tags = (
            select(
                post,
                func.array_agg(TagModel.name).label("tags"),
            ).outerjoin(
                association_table.join(TagModel),
                post.columns.id == association_table.columns.post_id,  # noqa
            )
        ).group_by(post)

        post = (await self.session.execute(post_with_tags)).mappings().one_or_none()
        if post is not None:
            return dict(post)

    async def add(self, username, data: dict) -> dict:
        tags = data.pop("tags")
        tags = await TagRepo(self.session).get_or_create(tags)

        record = await super().add(username, data)
        for tag in tags:
            record.tags.add(tag)

        return record.sync_dict()

    async def update(self, username, post_id, data) -> dict | None:
        tags = data.pop("tags")

        record = await super().update(username, post_id, data)
        if record is None:
            return

        if tags is not None:
            tags = await TagRepo(self.session).get_or_create(tags)
            record.tags.clear()
            for tag in tags:
                record.tags.add(tag)

        return record.sync_dict()

    async def get_post_with_url(self, username, url) -> dict | None:
        post = (
            select(self.model)
            .join(UserModel, self.model.username == username)
            .where(self.model.url == url)
        ).subquery("post")

        post_with_tags = (
            (
                select(
                    post,
                    func.array_agg(TagModel.name).label("tags"),
                ).outerjoin(
                    association_table.join(TagModel),
                    post.columns.id == association_table.columns.post_id,  # noqa
                )
            ).group_by(post)
        ).subquery("post_with_tags")

        all_comments_count = (
            (
                select(func.count("*"))
                .select_from(CommentModel)
                .where(CommentModel.post_id == post_with_tags.columns.id)
            )
            .scalar_subquery()
            .label("all_comments_count")
        )

        base_comments_count = (
            (
                select(func.count("*"))
                .select_from(CommentModel)
                .where(CommentModel.post_id == post_with_tags.columns.id)
                .where(CommentModel.parent_id == None)  # noqa: E711
            )
            .scalar_subquery()
            .label("base_comments_count")
        )

        reply_comments_count = (
            select(all_comments_count - base_comments_count)
            .scalar_subquery()
            .label("reply_comments_count")
        )
        stmt = select(
            post_with_tags,
            all_comments_count,
            base_comments_count,
            reply_comments_count,
        )
        post = (await self.session.execute(stmt)).mappings().one_or_none()
        if post is not None:
            return dict(post)

    async def list(
        self,
        username,
        *,
        page: int,
        per_page: int,
        sort: Sort,
        desc_: bool,
    ) -> list[dict]:
        """Return a list of Post objects

        This function paginates the results according to page and per_page
        This function sorts the results according to `Sort` and `SortOrder` values
        """
        order_by_column = self.model.title if sort is Sort.TITLE else self.model.created

        posts = (
            select(self.model)
            .where(self.model.username == username)
            .offset((page - 1) * per_page)
            .limit(per_page)
        ).subquery("posts")

        posts_with_tags = (
            (
                select(
                    posts,
                    func.array_agg(TagModel.name).label("tags"),
                ).outerjoin(
                    association_table.join(TagModel),
                    posts.columns.id == association_table.columns.post_id,  # noqa
                )
            )
            .group_by(posts)
            .order_by(
                desc(order_by_column) if desc_ else order_by_column,
            )
        )

        return list(
            map(
                dict,
                (await self.session.execute(posts_with_tags)).mappings().fetchall(),
            ),
        )
