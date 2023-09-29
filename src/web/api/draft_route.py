from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request

from src.repository.repos.draft_repo import DraftRepo
from src.repository.unit_of_work import UnitOfWork
from src.service.draft_service import DraftService
from src.web.api import give_domain
from src.web.core.dependencies import (
    get_current_user,
    QueryParameters,
    returning_query_parameters,
    get_db,
)
from src.web.core.schemas import (
    CreateDraftSchema,
    UserInternalSchema,
    DraftSchema,
    PublishSchema,
    PostSchema,
)

router = APIRouter(prefix="/drafts", tags=["drafts"])


@router.post(
    "/",
    response_model=DraftSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_draft(
    draft: CreateDraftSchema,
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UserInternalSchema, Depends(get_current_user)],
):
    """Create a draft draft"""
    async with UnitOfWork(session) as uow:
        repo = DraftRepo(uow.session)
        service = DraftService(repo)
        draft = await service.create_draft(user, draft.model_dump())
        await uow.commit()
        return draft.sync_dict()


@router.get(
    "/",
    response_model=list[DraftSchema],
    status_code=status.HTTP_200_OK,
)
async def get_drafts(
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UserInternalSchema, Depends(get_current_user)],
    query_parameters: Annotated[QueryParameters, Depends(returning_query_parameters)],
):
    """Retrieve all the draft"""
    async with UnitOfWork(session) as uow:
        repo = DraftRepo(uow.session)
        service = DraftService(repo)
        drafts = await service.list_drafts(
            user,
            page=query_parameters.page,
            per_page=query_parameters.per_page,
            sort=query_parameters.sort,
            desc_=query_parameters.desc,
        )
        return drafts


@router.get("/{draft_id}", response_model=DraftSchema, status_code=status.HTTP_200_OK)
async def get_draft(
    draft_id: int,
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UserInternalSchema, Depends(get_current_user)],
):
    """Return details of a specific draft"""
    async with UnitOfWork(session) as uow:
        repo = DraftRepo(uow.session)
        service = DraftService(repo)
        return await service.get_draft(user, draft_id)


@router.put("/{draft_id}", response_model=DraftSchema, status_code=status.HTTP_200_OK)
async def update_draft(
    draft_id: int,
    draft_detail: CreateDraftSchema,
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UserInternalSchema, Depends(get_current_user)],
):
    """Replace an existing draft"""
    async with UnitOfWork(session) as uow:
        repo = DraftRepo(uow.session)
        service = DraftService(repo)
        draft = await service.update_draft(user, draft_id, draft_detail.model_dump())
        await uow.commit()
        return draft.sync_dict()


@router.delete("/{draft_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_draft(
    draft_id: int,
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UserInternalSchema, Depends(get_current_user)],
):
    """Delete a specific draft"""
    async with UnitOfWork(session) as uow:
        repo = DraftRepo(uow.session)
        service = DraftService(repo)
        await service.delete_draft(user, draft_id)
        await uow.commit()


@router.post(
    "/{draft_id}/publish",
    status_code=status.HTTP_200_OK,
    response_model=PostSchema,
)
async def publish_draft(
    request: Request,
    draft_id: int,
    tags_and_title_in_url: PublishSchema,
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UserInternalSchema, Depends(get_current_user)],
):
    """Publish a draft post"""
    async with UnitOfWork(session) as uow:
        repo = DraftRepo(uow.session)
        service = DraftService(repo)
        post = await service.publish_draft(user, draft_id, tags_and_title_in_url)
        await uow.commit()
        post_data = post.sync_dict()
        post_data["comment_count"] = 0
        return give_domain(str(request.base_url), post_data)
