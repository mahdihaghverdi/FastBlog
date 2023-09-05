from typing import Annotated

from fastapi import Query, Depends
from sqlalchemy.ext.asyncio import async_sessionmaker
from starlette import status

from src.repository.posts_repository import PostsRepository
from src.repository.unit_of_work import UnitOfWork
from src.service.posts_service import PostsService
from src.web.api.schemas import Sort, PostSchema, CreatePostSchema
from src.web.app import app
from src.web.dependencies import get_async_sessionmaker


@app.get(
    "/posts",
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
        repo = PostsRepository(uow.session)
        service = PostsService(repo)
        posts = await service.list_posts(
            page=page,
            per_page=per_page,
            sort=sort,
            desc_=desc,
        )
        return posts


@app.post(
    "/posts",
    response_model=PostSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_post(
    post: CreatePostSchema,
    asessionmaker: Annotated[async_sessionmaker, Depends(get_async_sessionmaker)],
):
    """Create a post"""
    async with UnitOfWork(asessionmaker) as uow:
        repo = PostsRepository(uow.session)
        service = PostsService(repo)
        post = await service.create_post(post.model_dump())
        await uow.commit()
        payload = await post.dict()

    return payload
