from uuid import UUID

from src.common.exceptions import DraftNotFoundError
from src.service import Service
from src.service.objects import Draft
from src.web.core.schemas import Sort


class DraftService(Service):
    async def create_draft(self, user_id, draft: dict):
        return await self.repo.add(user_id, draft)

    async def list_drafts(
        self,
        user_id,
        *,
        page: int,
        per_page: int,
        sort: Sort,
        desc_: bool,
    ) -> list[Draft]:
        return await self.repo.list(
            user_id,
            page=page,
            per_page=per_page,
            sort=sort,
            desc_=desc_,
        )

    async def get_draft(self, user_id, draft_id) -> Draft:
        draft = await self.repo.get(user_id, draft_id)
        if draft is None:
            raise DraftNotFoundError(f"draft with id: '{draft_id}' is not found")
        return draft

    async def update_draft(self, user_id, draft_id: UUID, draft_detail: dict):
        draft = await self.repo.update(user_id, draft_id, draft_detail)
        if draft is None:
            raise DraftNotFoundError(f"draft with id: '{draft_id}' is not found")
        return draft

    async def delete_draft(self, user_id, draft_id):
        deleted = await self.repo.delete(user_id, draft_id)
        if deleted is False:
            raise DraftNotFoundError(f"draft with id: '{draft_id}' is not found")