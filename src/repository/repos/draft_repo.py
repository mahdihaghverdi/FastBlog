import itertools
from datetime import datetime

from slugify import Slugify
from sqlalchemy import select, desc

from src.repository.repos import BaseRepo, RelatedObjectsRepoMixin
from src.repository.models import DraftModel, UserModel, PostModel
from src.service.objects import Draft, Post
from src.web.core.schemas import Sort


class DraftRepo(RelatedObjectsRepoMixin, BaseRepo):
    def __init__(self, session):
        model = DraftModel
        object_ = Draft
        super().__init__(session, model, object_)

    async def list(
        self,
        user_id,
        *,
        page: int,
        per_page: int,
        sort: Sort,
        desc_: bool,
    ) -> list[Draft]:
        """Return a list of Post objects

        This function paginates the results according to page and per_page
        This function sorts the results according to `Sort` and `SortOrder` values
        """
        order_by_column = DraftModel.title if sort is Sort.TITLE else DraftModel.created
        stmt = (
            select(DraftModel)
            .where(DraftModel.user_id == user_id)
            .offset((page - 1) * per_page)
            .limit(per_page)
            .order_by(
                desc(order_by_column) if desc_ else order_by_column,
            )
        )
        records = list(
            itertools.chain.from_iterable((await self.session.execute(stmt)).all()),
        )
        return [Draft(**(await record.dict())) for record in records]

    async def publish(self, user: UserModel, draft_id, title_in_url):
        draft = await super(RelatedObjectsRepoMixin, self).get(draft_id, raw=True)
        if draft is None:
            return None
        slugify = Slugify(to_lower=True)
        if title_in_url is not None:
            title_slug = slugify(f"{title_in_url} {hex(hash(datetime.utcnow()))}")
        else:
            title_slug = slugify(f"{draft.title} {hex(hash(datetime.utcnow()))}")

        record = PostModel(
            title=draft.title,
            body=draft.body,
            url=f"/@{user.username}/{title_slug}",
        )
        self.session.add(record)
        user.posts.append(record)
        user.draft_posts.remove(draft)
        return Post(**(await record.dict()), model=record)
