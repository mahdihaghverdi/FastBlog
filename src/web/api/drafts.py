from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import async_sessionmaker
from starlette import status

from src.repository.draft_repo import DraftRepo
from src.repository.unit_of_work import UnitOfWork
from src.service.draft_service import DraftService
from src.web.core.dependencies import get_async_sessionmaker, get_current_user
from src.web.core.schemas import (
    CreateDraftSchema,
    UserInternalSchema,
    Sort,
    DraftSchema,
)

router = APIRouter(prefix="/drafts", tags=["drafts"])


@router.post(
    "/",
    response_model=DraftSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_draft(
    draft: CreateDraftSchema,
    asessionmaker: Annotated[async_sessionmaker, Depends(get_async_sessionmaker)],
    user: Annotated[UserInternalSchema, Depends(get_current_user)],
):
    """Create a draft draft"""
    async with UnitOfWork(asessionmaker) as uow:
        repo = DraftRepo(uow.session)
        service = DraftService(repo)
        draft = await service.create_draft(user.id, draft.model_dump())
        await uow.commit()
        payload = await draft.dict()

    return payload


@router.get(
    "/",
    response_model=list[DraftSchema],
    status_code=status.HTTP_200_OK,
)
async def get_drafts(
    asessionmaker: Annotated[async_sessionmaker, Depends(get_async_sessionmaker)],
    user: Annotated[UserInternalSchema, Depends(get_current_user)],
    page: Annotated[
        int,
        Query(description="page number of the pagination", ge=1),
    ] = 1,
    per_page: Annotated[
        int,
        Query(
            alias="per-page",
            description="number of posts per page",
            ge=1,
            le=30,
        ),
    ] = 5,
    sort: Annotated[
        Sort,
        Query(description="sorts the returned posts"),
    ] = Sort.DATE,
    desc: Annotated[
        bool,
        Query(description="order of the sorted posts"),
    ] = True,
):
    """Retrieve all the draft"""
    async with UnitOfWork(asessionmaker) as uow:
        repo = DraftRepo(uow.session)
        service = DraftService(repo)
        drafts = await service.list_drafts(
            user.id,
            page=page,
            per_page=per_page,
            sort=sort,
            desc_=desc,
        )
        return drafts


@router.get("/{draft_id}", response_model=DraftSchema, status_code=status.HTTP_200_OK)
async def get_draft(
    draft_id: UUID,
    asessionmaker: Annotated[async_sessionmaker, Depends(get_async_sessionmaker)],
    user: Annotated[UserInternalSchema, Depends(get_current_user)],
):
    """Return details of a specific draft"""
    async with UnitOfWork(asessionmaker) as uow:
        repo = DraftRepo(uow.session)
        service = DraftService(repo)
        return await service.get_draft(user.id, draft_id)


@router.put("/{draft_id}", response_model=DraftSchema, status_code=status.HTTP_200_OK)
async def update_post(
    draft_id: UUID,
    draft_detail: CreateDraftSchema,
    asessionmaker: Annotated[async_sessionmaker, Depends(get_async_sessionmaker)],
    user: Annotated[UserInternalSchema, Depends(get_current_user)],
):
    """Replace an existing draft"""
    async with UnitOfWork(asessionmaker) as uow:
        repo = DraftRepo(uow.session)
        service = DraftService(repo)
        draft = await service.update_draft(user.id, draft_id, draft_detail.model_dump())
        await uow.commit()
        return await draft.dict()


@router.delete("/{draft_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    draft_id: UUID,
    asessionmaker: Annotated[async_sessionmaker, Depends(get_async_sessionmaker)],
    user: Annotated[UserInternalSchema, Depends(get_current_user)],
):
    """Delete a specific draft"""
    async with UnitOfWork(asessionmaker) as uow:
        repo = DraftRepo(uow.session)
        service = DraftService(repo)
        await service.delete_draft(user.id, draft_id)
        await uow.commit()
