from typing import Annotated

from fastapi import APIRouter, Depends, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from src.repository.repos.comment_repo import CommentRepo
from src.repository.repos.post_repo import PostRepo
from src.repository.unit_of_work import UnitOfWork
from src.service.comment_service import CommentService
from src.web.core.dependencies import get_db, get_current_user
from src.web.core.schemas import CommentSchema, ReplyLevel, UserInternalSchema

router = APIRouter(prefix="/comments", tags=["comments"])


# TODO: write tests for PostNotFoundError
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
        post_repo = PostRepo(uow.session)
        service = CommentService(repo, post_repo=post_repo)
        comments = await service.get_comments(
            post_id=post_id,
            comment_id=0,
            reply_level=reply_level,
        )
        return comments


# TODO: write tests for PostNotFoundError
@router.get(
    "/{post_id}/{comment_id}",
    response_model=list[CommentSchema],
    status_code=status.HTTP_200_OK,
)
async def get_replies(
    post_id: int,
    comment_id: int,
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
        post_repo = PostRepo(uow.session)
        service = CommentService(repo, post_repo=post_repo)
        comments = await service.get_comments(
            post_id=post_id,
            comment_id=comment_id,
            reply_level=reply_level,
        )
        return comments


@router.put(
    "/{post_id}/{comment_id}",
    response_model=CommentSchema,
    status_code=status.HTTP_200_OK,
)
async def update_comment(
    post_id: int,
    comment_id: int,
    comment: Annotated[str, Body(min_length=1, max_length=255)],
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UserInternalSchema, Depends(get_current_user)],
):
    async with UnitOfWork(session) as uow:
        repo = CommentRepo(uow.session)
        post_repo = PostRepo(uow.session)
        service = CommentService(repo, post_repo=post_repo)
        comment = await service.update_comment(
            username=user.username,
            post_id=post_id,
            comment_id=comment_id,
            comment=comment,
        )
        await uow.commit()
        return comment


@router.delete(
    "/{post_id}/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_comment(
    post_id: int,
    comment_id: int,
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UserInternalSchema, Depends(get_current_user)],
):
    async with UnitOfWork(session) as uow:
        repo = CommentRepo(uow.session)
        post_repo = PostRepo(uow.session)
        service = CommentService(repo, post_repo=post_repo)
        await service.delete_comment(
            username=user.username,
            post_id=post_id,
            comment_id=comment_id,
        )
        await uow.commit()
