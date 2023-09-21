from sqlalchemy import select, desc
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
            setattr(record, key, value)
        self.session.add(record)
        return Post(**record.sync_dict(), model=record)

    async def get_post_of_someone_with_comments(self, user_id, url):
        stmt = (
            select(PostModel, CommentModel)
            .options(joinedload(PostModel.tags))
            .join(UserModel.posts.and_(PostModel.user_id == user_id))
            .where(PostModel.url == url)
            .join(CommentModel, CommentModel.post_id == PostModel.id)
            .where(CommentModel.parent_id == None)  # noqa: E711
            .order_by(desc(CommentModel.created))
            .limit(5)
            .execution_options(populate_existing=True)
        )
        posts = (await self.session.execute(stmt)).unique().fetchall()
        if posts:
            comments = []
            post_model, *_ = posts[0].tuple()

            # get comments count
            # sub = select('*').where(CommentModel.post_id == post_model.id)
            # stmt = select(func.count()).select_from(sub.subquery())
            # all_comments_count = (await self.session.execute(stmt)).scalar()

            for post in posts:
                *_, comment_model = post.tuple()
                comments.append(comment_model.sync_dict())
            return post_model.sync_dict(), comments
