from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import async_sessionmaker
from starlette import status

from src.repository.post_repository import PostRepo
from src.repository.unit_of_work import UnitOfWork
from src.service.post_service import PostService
from src.web.core.schemas import CreatePostSchema, PostSchema, Sort
from src.web.core.dependencies import get_async_sessionmaker

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get(
    "/",
    response_model=list[PostSchema],
    status_code=status.HTTP_200_OK,
)
async def get_posts(
    asessionmaker: Annotated[async_sessionmaker, Depends(get_async_sessionmaker)],
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
    """Retrieve all the posts"""
    async with UnitOfWork(asessionmaker) as uow:
        repo = PostRepo(uow.session)
        service = PostService(repo)
        posts = await service.list_posts(
            page=page,
            per_page=per_page,
            sort=sort,
            desc_=desc,
        )
        return posts


@router.post(
    "/",
    response_model=PostSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_post(
    post: CreatePostSchema,
    asessionmaker: Annotated[async_sessionmaker, Depends(get_async_sessionmaker)],
):
    """Create a post"""
    async with UnitOfWork(asessionmaker) as uow:
        repo = PostRepo(uow.session)
        service = PostService(repo)
        post = await service.create_post(post.model_dump())
        await uow.commit()
        payload = await post.dict()

    return payload


@router.get("/{post_id}", response_model=PostSchema, status_code=status.HTTP_200_OK)
async def get_post(
    post_id: UUID,
    asessionmaker: Annotated[async_sessionmaker, Depends(get_async_sessionmaker)],
):
    """Return details of a specific post"""
    async with UnitOfWork(asessionmaker) as uow:
        repo = PostRepo(uow.session)
        service = PostService(repo)
        return await (await service.get_post(post_id)).dict()


@router.put("/{post_id}", response_model=PostSchema, status_code=status.HTTP_200_OK)
async def update_post(
    post_id: UUID,
    post_detail: CreatePostSchema,
    asessionmaker: Annotated[async_sessionmaker, Depends(get_async_sessionmaker)],
):
    """Replace an existing post"""
    async with UnitOfWork(asessionmaker) as uow:
        repo = PostRepo(uow.session)
        service = PostService(repo)
        post = await service.update_post(post_id, post_detail.model_dump())
        await uow.commit()
        return await post.dict()


@router.delete("/{post_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_post(
    post_id: UUID,
    asessionmaker: Annotated[async_sessionmaker, Depends(get_async_sessionmaker)],
):
    """Delete a specific post"""
    async with UnitOfWork(asessionmaker) as uow:
        repo = PostRepo(uow.session)
        service = PostService(repo)
        await service.delete_post(post_id)
        await uow.commit()
