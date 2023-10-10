import itertools

from sqlalchemy import desc, select

from src.repository.models import DraftModel, PostModel
from src.repository.repos import BaseRepo, OneToManyRelRepoMixin
from src.repository.repos.tag_repo import TagRepo
from src.service.objects import Draft, Post
from src.web.core.schemas import Sort


class DraftRepo(OneToManyRelRepoMixin, BaseRepo):
    def __init__(self, session):
        model = DraftModel
        object_ = Draft
        super().__init__(session, model, object_)

    async def list(
        self,
        username,
        *,
        page: int,
        per_page: int,
        sort: Sort,
        desc_: bool,
    ) -> list:
        """Return a list of Post objects

        This function paginates the results according to page and per_page
        This function sorts the results according to `Sort` and `SortOrder` values
        """
        order_by_column = DraftModel.title if sort is Sort.TITLE else DraftModel.created
        stmt = (
            select(DraftModel)
            .where(DraftModel.username == username)
            .offset((page - 1) * per_page)
            .limit(per_page)
            .order_by(
                desc(order_by_column) if desc_ else order_by_column,
            )
        )
        records = list(
            itertools.chain.from_iterable((await self.session.execute(stmt)).all()),
        )
        return [self.object(**record.sync_dict(), model=record) for record in records]

    async def publish(self, user, draft_id, tags_and_title_in_url):
        draft = await super(OneToManyRelRepoMixin, self).get(draft_id)
        if draft is None:
            return None

        slug = tags_and_title_in_url.slug(draft.title, user.username)
        tags = await TagRepo(self.session).get_or_create(tags_and_title_in_url.tags)

        record = PostModel(title=draft.title, body=draft.body, url=f"{slug}")
        for tag in tags:
            record.tags.add(tag)

        self.session.add(record)
        user.posts.append(record)
        user.drafts.remove(draft)
        return Post(**record.sync_dict(), model=record)
