from src.common.exceptions import DraftNotFoundError
from src.repository.repos.user_repo import UserRepo
from src.service import Service
from src.service.objects import Draft
from src.web.core.schemas import Sort


class DraftService(Service):
    async def create_draft(self, user, draft: dict):
        return await self.repo.add(user.username, draft)

    async def list_drafts(
        self,
        user,
        *,
        page: int,
        per_page: int,
        sort: Sort,
        desc_: bool,
    ) -> list[Draft]:
        return await self.repo.list(
            user.username,
            page=page,
            per_page=per_page,
            sort=sort,
            desc_=desc_,
        )

    async def get_draft(self, user, draft_id) -> Draft:
        draft = await self.repo.get(user.username, draft_id)
        if draft is None:
            raise DraftNotFoundError(draft_id)
        return draft

    async def update_draft(self, user, draft_id, draft_detail: dict):
        draft = await self.repo.update(user.username, draft_id, draft_detail)
        if draft is None:
            raise DraftNotFoundError(draft_id)
        return draft

    async def delete_draft(self, user, draft_id):
        deleted = await self.repo.delete(user.username, draft_id)
        if deleted is False:
            raise DraftNotFoundError(draft_id)

    async def publish_draft(self, user, draft_id, tags_and_title_in_url):
        user = await UserRepo(self.repo.session).get(user.id, raw=True)
        post = await self.repo.publish(user, draft_id, tags_and_title_in_url)
        if post is None:
            raise DraftNotFoundError(draft_id)
        return post
