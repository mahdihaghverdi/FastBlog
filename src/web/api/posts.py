from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import async_sessionmaker
from starlette import status
from starlette.requests import Request

from src.repository.repos.post_repo import PostRepo
from src.repository.unit_of_work import UnitOfWork
from src.service.post_service import PostService
from src.web.core.dependencies import get_async_sessionmaker, get_current_user
from src.web.core.schemas import CreatePostSchema, PostSchema, Sort, UserInternalSchema
from . import give_domain

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

        slug = post.slug(user.username)
        post_dict = post.model_dump()
        del post_dict["title_in_url"]
        post_dict["url"] = slug
        post = await service.create_post(user.id, post_dict)
        await uow.commit()
        return give_domain(str(request.base_url), await post.dict())


@router.get(
    "/",
    response_model=list[PostSchema],
    status_code=status.HTTP_200_OK,
)
async def get_posts(
    request: Request,
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
    """Retrieve all the posts"""
    async with UnitOfWork(asessionmaker) as uow:
        repo = PostRepo(uow.session)
        service = PostService(repo)
        posts = await service.list_posts(
            user.id,
            page=page,
            per_page=per_page,
            sort=sort,
            desc_=desc,
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
    post_detail: CreatePostSchema,
    asessionmaker: Annotated[async_sessionmaker, Depends(get_async_sessionmaker)],
    user: Annotated[UserInternalSchema, Depends(get_current_user)],
):
    """Replace an existing post"""
    # TODO: test title_in_url in this fucking route
    async with UnitOfWork(asessionmaker) as uow:
        repo = PostRepo(uow.session)
        service = PostService(repo)
        post = await service.update_post(user.id, post_id, post_detail.model_dump())
        await uow.commit()
        return give_domain(str(request.base_url), await post.dict())


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
