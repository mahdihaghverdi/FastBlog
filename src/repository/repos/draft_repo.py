from src.repository.models import DraftModel, PostModel
from src.repository.repos import BaseRepo, OneToManyRelRepoMixin, PaginationMixin
from src.repository.repos.tag_repo import TagRepo
from src.service.objects import Draft, Post


class DraftRepo(PaginationMixin, OneToManyRelRepoMixin, BaseRepo):
    def __init__(self, session):
        model = DraftModel
        object_ = Draft
        super().__init__(session, model, object_)

    async def publish(self, user, draft_id, tags_and_title_in_url):
        draft = await super(OneToManyRelRepoMixin, self).get(draft_id, raw=True)
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
