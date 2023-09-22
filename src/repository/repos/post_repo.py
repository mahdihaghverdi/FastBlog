from sqlalchemy import select, desc, func, String, cast
from sqlalchemy.orm import joinedload
from sqlalchemy.sql import expression
from sqlalchemy_utils.types.ltree import LQUERY

from src.repository.models import PostModel, UserModel, CommentModel
from src.repository.repos import BaseRepo, OneToManyRelRepoMixin, PaginationMixin
from src.repository.repos.tag_repo import TagRepo
from src.service.objects import Post, Comment


class PostRepo(PaginationMixin, OneToManyRelRepoMixin, BaseRepo):
    def __init__(self, session):
        model = PostModel
        object_ = Post
        super().__init__(session, model, object_)

    async def add(self, user_id, data: dict):
        # get or create tags
        tags = data.pop("tags")
        tags = await TagRepo(self.session).get_or_create(tags)

        record = self.model(**data, user_id=user_id)
        for tag in tags:
            record.tags.add(tag)
        self.session.add(record)
        return Post(**record.sync_dict(), model=record)

    async def update(self, user_id, post_id, data: dict):
        record = await self._get(user_id, post_id)
        if record is None:
            return

        tags = data.pop("tags")
        tags = await TagRepo(self.session).get_or_create(tags)
        record.tags.clear()
        for tag in tags:
            record.tags.add(tag)

        for key, value in data.items():
            setattr(record, key, value)
        self.session.add(record)
        return Post(**record.sync_dict(), model=record)

    async def get_post_of_someone_with_comments(self, user_id, url):
        post_stmt = (
            select(PostModel)
            .options(joinedload(PostModel.tags))
            .join(UserModel.posts.and_(PostModel.user_id == user_id))
            .where(PostModel.url == url)
        )
        post = (await self.session.execute(post_stmt)).unique().scalar_one_or_none()
        if post is None:
            return None

        # select
        #   *,
        #   (
        #     select
        #       count(*)
        #     from
        #       comments
        #     where
        #       path ~ CONCAT(a.path :: varchar, '.*{1}'):: lquery
        #   )
        # from
        #   (
        #     select
        #       comments.*
        #     from
        #       comments
        #       join posts on posts.id = comments.post_id
        #     where
        #       parent_id is null
        #   ) a;

        comments_subquery = (
            select(
                CommentModel.id,
                CommentModel.created,
                CommentModel.post_id,
                CommentModel.parent_id,
                CommentModel.comment,
                CommentModel.user_id,
                cast(CommentModel.path, String),
                UserModel.username,
            )
            .join(PostModel, CommentModel.post_id == post.id)
            .where(CommentModel.parent_id == None)  # noqa: E711
            .join(UserModel)
            .order_by(desc(CommentModel.created))
            .limit(5)
        ).subquery()
        count_stmt = (
            select(func.count())
            .filter(
                CommentModel.path.lquery(
                    expression.cast(
                        expression.cast(comments_subquery.columns.path, String)
                        + ".*{1}",
                        LQUERY,
                    ),
                ),
            )
            .scalar_subquery()
        )
        stmt = select(comments_subquery, count_stmt.label("reply_count"))

        result = (await self.session.execute(stmt)).unique().mappings().all()
        comments = list(Comment(**data) for data in result)
        return post, comments
