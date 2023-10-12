from typing import Annotated

from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request

from src.repository.repos.comment_repo import CommentRepo
from src.repository.repos.post_repo import PostRepo
from src.repository.unit_of_work import UnitOfWork
from src.service.comment_service import CommentService
from src.service.post_service import PostService
from src.web.api import give_domain
from src.web.core.dependencies import (
    get_db,
    get_current_user_simple,
    returning_query_parameters,
    QueryParameters,
)
from src.web.core.schemas import (
    CreatePostSchema,
    PostSchema,
    UserInternalSchema,
    CommentSchema,
    UpdatePostSchema,
)

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post(
    "/",
    response_model=PostSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_post(
    request: Request,
    post: CreatePostSchema,
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UserInternalSchema, Depends(get_current_user_simple)],
):
    """Create a post"""
    async with UnitOfWork(session) as uow:
        repo = PostRepo(uow.session)
        service = PostService(repo)
        post = await service.create_post(user.username, post)
        await uow.commit()
        return give_domain(str(request.base_url), post)


@router.get(
    "/",
    response_model=list[PostSchema],
    status_code=status.HTTP_200_OK,
)
async def get_posts(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UserInternalSchema, Depends(get_current_user_simple)],
    query_parameters: Annotated[QueryParameters, Depends(returning_query_parameters)],
):
    """Retrieve all the posts"""
    async with UnitOfWork(session) as uow:
        repo = PostRepo(uow.session)
        service = PostService(repo)
        posts = await service.list_posts(
            user.username,
            page=query_parameters.page,
            per_page=query_parameters.per_page,
            sort=query_parameters.sort,
            desc_=query_parameters.desc,
        )
        posts = give_domain(str(request.base_url), posts)
        return posts


@router.get("/{post_id}", response_model=PostSchema, status_code=status.HTTP_200_OK)
async def get_post(
    request: Request,
    post_id: int,
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UserInternalSchema, Depends(get_current_user_simple)],
):
    """Return details of a specific post"""
    async with UnitOfWork(session) as uow:
        repo = PostRepo(uow.session)
        service = PostService(repo)
        post = await service.get_post(user.username, post_id)
        payload = give_domain(str(request.base_url), post)
        return payload


@router.patch(
    "/{post_id}",
    response_model=PostSchema,
    status_code=status.HTTP_200_OK,
)
async def update_post(
    request: Request,
    post_id: int,
    post: UpdatePostSchema,
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UserInternalSchema, Depends(get_current_user_simple)],
):
    """Updating a post"""
    async with UnitOfWork(session) as uow:
        repo = PostRepo(uow.session)
        service = PostService(repo)
        post = await service.update_post(user.username, post_id, post)
        await uow.commit()
        return give_domain(str(request.base_url), post)


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UserInternalSchema, Depends(get_current_user_simple)],
):
    """Delete a specific post"""
    async with UnitOfWork(session) as uow:
        repo = PostRepo(uow.session)
        service = PostService(repo)
        await service.delete_post(user.username, post_id)
        await uow.commit()


@router.post(
    "/{post_id}/comment",
    status_code=status.HTTP_201_CREATED,
    response_model=CommentSchema,
)
async def add_comment(
    post_id: int,
    comment: Annotated[str, Body(min_length=1, max_length=255)],
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UserInternalSchema, Depends(get_current_user_simple)],
):
    async with UnitOfWork(session) as uow:
        repo = PostRepo(uow.session)
        comment_repo = CommentRepo(uow.session)
        service = PostService(repo=repo, comment_repo=comment_repo)
        comment = await service.add_comment(user.username, post_id, comment)
        await uow.commit()
        return comment


@router.post(
    "/{post_id}/comment/{comment_id}",
    status_code=status.HTTP_201_CREATED,
    response_model=CommentSchema,
)
async def add_reply(
    post_id: int,
    comment_id: int,
    reply: Annotated[str, Body(min_length=1, max_length=255)],
    session: Annotated[AsyncSession, Depends(get_db)],
    user: Annotated[UserInternalSchema, Depends(get_current_user_simple)],
):
    async with UnitOfWork(session) as uow:
        repo = CommentRepo(uow.session)
        post_repo = PostRepo(uow.session)
        service = CommentService(repo, post_repo=post_repo)
        comment = await service.reply(
            username=user.username,
            post_id=post_id,
            comment_id=comment_id,
            reply=reply,
        )
        await uow.commit()
        return comment
