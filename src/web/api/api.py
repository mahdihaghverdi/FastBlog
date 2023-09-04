from typing import Annotated

from fastapi import Query
from starlette import status

from src.web.api.schemas import Sort, SortOrder, PostSchema, CreatePostSchema
from src.web.app import app


@app.get(
    "/posts",
    response_model=list[PostSchema],
    status_code=status.HTTP_200_OK,
)
async def get_posts(
    page: Annotated[
        int,
        Query(
            description="page number of the pagination",
            ge=1,
        ),
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
    order: Annotated[
        SortOrder,
        Query(description="order of the sorted posts"),
    ] = SortOrder.DESC,
):
    """Retrieve all the posts"""


@app.post(
    "/posts",
    response_model=PostSchema,
    status_code=status.HTTP_201_CREATED,
)
async def create_post(post: CreatePostSchema):
    """Create a post"""
