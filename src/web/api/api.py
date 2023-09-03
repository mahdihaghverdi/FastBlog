from typing import Annotated

from fastapi import Query

from src.web.api.schemas import Sort, Order
from src.web.app import app


@app.get("/posts")
async def get_posts(
    page: Annotated[
        int | None,
        Query(description="page number of the pagination", ge=1),
    ] = 1,
    per_page: Annotated[
        int | None,
        Query(alias="per-page", description="number of posts per page", ge=1, le=30),
    ] = 5,
    sort: Annotated[Sort, Query(description="sorts the returned posts")] = Sort.DATE,
    order: Annotated[
        Order,
        Query(description="order of the sorted posts"),
    ] = Order.DESC,
):
    """Retrieve all the posts"""
