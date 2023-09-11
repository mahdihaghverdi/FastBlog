from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import async_sessionmaker
from starlette import status

from src.repository.draft_post_repo import DraftPostRepo
from src.repository.unit_of_work import UnitOfWork
from src.service.draft_post_service import DraftPostService
from src.web.core.dependencies import get_async_sessionmaker, get_current_user
from src.web.core.schemas import PostSchema, CreatePostSchema, UserInternalSchema

router = APIRouter(prefix="/drafts", tags=["drafts"])


@router.post(
    "/",
    response_model=PostSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_draft_post(
    post: CreatePostSchema,
    asessionmaker: Annotated[async_sessionmaker, Depends(get_async_sessionmaker)],
    user: Annotated[UserInternalSchema, Depends(get_current_user)],
):
    """Create a draft post"""
    async with UnitOfWork(asessionmaker) as uow:
        repo = DraftPostRepo(uow.session)
        service = DraftPostService(repo)
        post = await service.create_draft_post(user.id, post.model_dump())
        await uow.commit()
        payload = await post.dict()

    return payload
