from typing import Annotated

from fastapi import APIRouter, Depends, Body
from sqlalchemy.ext.asyncio import async_sessionmaker
from starlette import status
from starlette.requests import Request

from src.repository.repos.post_repo import PostRepo
from src.repository.unit_of_work import UnitOfWork
from src.service.post_service import PostService
from src.web.core.dependencies import (
    get_async_sessionmaker,
    get_current_user,
    returning_query_parameters,
    QueryParameters,
)
from src.web.core.schemas import CreatePostSchema, PostSchema, UserInternalSchema
from . import give_domain
from ..core.schemas.comment_schema import CommentSchema
from ...repository.repos.comment_repo import CommentRepo

router = APIRouter(prefix="/posts", tags=["posts"])


@router.post(
    "/",
    response_model=PostSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_post(
    request: Request,
    post: CreatePostSchema,
    asessionmaker: Annotated[async_sessionmaker, Depends(get_async_sessionmaker)],
    user: Annotated[UserInternalSchema, Depends(get_current_user)],
):
    """Create a post"""
    async with UnitOfWork(asessionmaker) as uow:
        repo = PostRepo(uow.session)
        service = PostService(repo)
        post = await service.create_post(user, post)
        await uow.commit()
        return give_domain(str(request.base_url), post.sync_dict())


@router.get(
    "/",
    response_model=list[PostSchema],
    status_code=status.HTTP_200_OK,
)
async def get_posts(
    request: Request,
    asessionmaker: Annotated[async_sessionmaker, Depends(get_async_sessionmaker)],
    user: Annotated[UserInternalSchema, Depends(get_current_user)],
    query_parameters: Annotated[QueryParameters, Depends(returning_query_parameters)],
):
    """Retrieve all the posts"""
    async with UnitOfWork(asessionmaker) as uow:
        repo = PostRepo(uow.session)
        service = PostService(repo)
        posts = await service.list_posts(
            user.id,
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
    asessionmaker: Annotated[async_sessionmaker, Depends(get_async_sessionmaker)],
    user: Annotated[UserInternalSchema, Depends(get_current_user)],
):
    """Return details of a specific post"""
    async with UnitOfWork(asessionmaker) as uow:
        repo = PostRepo(uow.session)
        service = PostService(repo)
        post = await service.get_post(user.id, post_id)
        payload = give_domain(str(request.base_url), post)
        return payload


@router.put("/{post_id}", response_model=PostSchema, status_code=status.HTTP_200_OK)
async def update_post(
    request: Request,
    post_id: int,
    post: CreatePostSchema,
    asessionmaker: Annotated[async_sessionmaker, Depends(get_async_sessionmaker)],
    user: Annotated[UserInternalSchema, Depends(get_current_user)],
):
    """Replace an existing post"""
    async with UnitOfWork(asessionmaker) as uow:
        repo = PostRepo(uow.session)
        service = PostService(repo)
        post = await service.update_post(user, post_id, post)
        await uow.commit()
        return give_domain(str(request.base_url), post.sync_dict())


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: int,
    asessionmaker: Annotated[async_sessionmaker, Depends(get_async_sessionmaker)],
    user: Annotated[UserInternalSchema, Depends(get_current_user)],
):
    """Delete a specific post"""
    async with UnitOfWork(asessionmaker) as uow:
        repo = PostRepo(uow.session)
        service = PostService(repo)
        await service.delete_post(user.id, post_id)
        await uow.commit()


@router.post(
    "/{post_id}/comment",
    status_code=status.HTTP_201_CREATED,
    response_model=CommentSchema,
)
async def add_comment(
    post_id: int,
    comment: Annotated[str, Body(min_length=1, max_length=255)],
    asessionmaker: Annotated[async_sessionmaker, Depends(get_async_sessionmaker)],
    user: Annotated[UserInternalSchema, Depends(get_current_user)],  # noqa
):
    async with UnitOfWork(asessionmaker) as uow:
        repo = CommentRepo(uow.session)
        service = PostService(repo=None, comment_repo=repo)
        comment = await service.add_comment(post_id, comment)
        await uow.commit()
        return comment.sync_dict()
