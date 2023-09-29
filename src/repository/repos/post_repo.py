from sqlalchemy import select, func, insert, desc
from sqlalchemy.orm import joinedload

from src.repository.models import (
    PostModel,
    UserModel,
    CommentModel,
    TagModel,
    association_table,
)
from src.repository.repos import BaseRepo, OneToManyRelRepoMixin, PaginationMixin
from src.repository.repos.tag_repo import TagRepo
from src.service.objects import Post
from src.web.core.schemas import Sort


class PostRepo(PaginationMixin, OneToManyRelRepoMixin, BaseRepo):
    def __init__(self, session):
        model = PostModel
        object_ = Post
        super().__init__(session, model, object_)

    async def get(self, username, self_id):
        post = (
            select(PostModel)
            .where(PostModel.id == self_id)
            .where(PostModel.username == username)
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

        comment_count = (
            (
                select(func.count("*"))
                .select_from(CommentModel)
                .where(CommentModel.post_id == post_with_tags.columns.id)
            )
            .scalar_subquery()
            .label("comment_count")
        )

        stmt = select(post_with_tags, comment_count)
        post = (await self.session.execute(stmt)).mappings().one_or_none()
        if post is not None:
            return dict(post)

    async def add(self, username, data: dict):
        # get or create tags
        tags = data.pop("tags")
        tags = await TagRepo(self.session).get_or_create(tags)

        stmt = insert(PostModel).values(**data, username=username).returning(PostModel)
        record = (await self.session.execute(stmt)).scalar_one_or_none()
        for tag in tags:
            record.tags.add(tag)

        to_ret = record.sync_dict()
        to_ret["comment_count"] = 0
        return to_ret

    async def update(self, username, post_id, data: dict):
        record = await self._get(username, post_id)
        if record is None:
            return

        tags = data.pop("tags")
        if tags is not None:
            tags = await TagRepo(self.session).get_or_create(tags)
            record.tags.clear()
            for tag in tags:
                record.tags.add(tag)

        data = {k: v for k, v in data.items() if v is not None}
        for key, value in data.items():
            setattr(record, key, value)
        self.session.add(record)
        return Post(**record.sync_dict(), model=record)

    async def get_post_with_url(self, username, url):
        post_stmt = (
            select(PostModel)
            .join(UserModel, PostModel.username == username)
            .where(PostModel.url == url)
        ).subquery()

        comment_count = self._comment_count_scalar_subquery(post_stmt)

        tags = (
            select(PostModel)
            .options(joinedload(PostModel.tags))
            .where(PostModel.id == post_stmt.columns.id)
        )
        post_and_comment_count = select(post_stmt, comment_count)

        post = (
            (await self.session.execute(post_and_comment_count))
            .unique()
            .mappings()
            .fetchall()
        )
        if post:
            tags = (
                (await self.session.execute(tags))
                .unique()
                .scalar_one()
                .sync_dict()["tags"]
            )
            to_ret = dict(post[0])
            to_ret["tags"] = tags
            return dict(to_ret)

    @staticmethod
    def _comment_count_scalar_subquery(post_stmt):
        comment_count = (
            (
                select(func.count("*"))
                .select_from(CommentModel)
                .join(PostModel, PostModel.id == CommentModel.post_id)
                .where(CommentModel.post_id == post_stmt.columns.id)
            )
            .scalar_subquery()
            .label("comment_count")
        )
        return comment_count

    async def list(
        self,
        username,
        *,
        page: int,
        per_page: int,
        sort: Sort,
        desc_: bool,
    ):
        """Return a list of Post objects

        This function paginates the results according to page and per_page
        This function sorts the results according to `Sort` and `SortOrder` values
        """
        order_by_column = PostModel.title if sort is Sort.TITLE else self.model.created

        posts = (
            select(PostModel)
            .where(PostModel.username == username)
            .offset((page - 1) * per_page)
            .limit(per_page)
            .order_by(
                desc(order_by_column) if desc_ else order_by_column,
            )
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
            .order_by(posts.columns.created)
        ).subquery("posts_with_tags")

        comment_count = (
            (
                select(func.count("*"))
                .select_from(CommentModel)
                .where(CommentModel.post_id == posts_with_tags.columns.id)
            )
            .scalar_subquery()
            .label("comment_count")
        )

        stmt = select(posts_with_tags, comment_count)
        return list(map(dict, (await self.session.execute(stmt)).mappings().fetchall()))
