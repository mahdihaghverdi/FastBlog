from sqlalchemy import select, func
from sqlalchemy.orm import joinedload

from src.repository.models import PostModel, UserModel, CommentModel
from src.repository.repos import BaseRepo, OneToManyRelRepoMixin, PaginationMixin
from src.repository.repos.tag_repo import TagRepo
from src.service.objects import Post


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
            if key == "url" and value is None:
                continue
            setattr(record, key, value)
        self.session.add(record)
        return Post(**record.sync_dict(), model=record)

    async def get_post_with_url(self, user_id, url):
        post_stmt = (
            select(PostModel)
            .join(UserModel, PostModel.user_id == user_id)
            .where(PostModel.url == url)
        ).subquery()

        # select count(*)
        # from comments
        # join posts on posts.id = post_id
        # where post_id = ?
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
