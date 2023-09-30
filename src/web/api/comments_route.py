from typing import Annotated

from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.repository.repos.comment_repo import CommentRepo
from src.repository.unit_of_work import UnitOfWork
from src.service.comment_service import CommentService
from src.web.core.dependencies import get_db
from src.web.core.schemas import CommentSchema, ReplyLevel

router = APIRouter(prefix="/comments", tags=["comments"])


@router.get(
    "/{post_id}/basecomments",
    response_model=list[CommentSchema],
    status_code=status.HTTP_200_OK,
)
async def get_base_comments(
    post_id: int,
    session: Annotated[AsyncSession, Depends(get_db)],
    reply_level: Annotated[
        ReplyLevel,
        Query(
            alias="reply-level",
            description="how many nested replies should be returned",
        ),
    ] = ReplyLevel.BASE,
):
    async with UnitOfWork(session) as uow:
        repo = CommentRepo(uow.session)
        service = CommentService(repo)
        comments = await service.get_comments(
            post_id,
            0,
            reply_level=reply_level,
        )
        return comments


@router.get(
    "/{post_id}/{comment_id}",
    response_model=list[CommentSchema],
    status_code=status.HTTP_200_OK,
)
async def get_comments(
    post_id: int,
    comment_id: Annotated[int, Path()],
    session: Annotated[AsyncSession, Depends(get_db)],
    reply_level: Annotated[
        ReplyLevel,
        Query(
            alias="reply-level",
            description="how many nested replies should be returned",
        ),
    ] = ReplyLevel.BASE,
):
    async with UnitOfWork(session) as uow:
        repo = CommentRepo(uow.session)
        service = CommentService(repo)
        comments = await service.get_comments(
            post_id,
            comment_id,
            reply_level=reply_level,
        )
        return comments
