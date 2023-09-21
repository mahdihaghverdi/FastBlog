from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import async_sessionmaker
from starlette.requests import Request

from src.repository.repos.post_repo import PostRepo
from src.repository.unit_of_work import UnitOfWork
from src.service.post_service import PostService
from src.web.core.dependencies import get_async_sessionmaker
from src.web.core.schemas import PostSchema
from . import give_domain
from ...repository.repos.user_repo import UserRepo

router = APIRouter(tags=["global posts"])


@router.get("/@{username}/{post_slug}", response_model=PostSchema)
async def get_global_post(
    username: str,
    post_slug: str,
    request: Request,
    asessionmaker: Annotated[async_sessionmaker, Depends(get_async_sessionmaker)],
):
    async with UnitOfWork(asessionmaker) as uow:
        post_repo = PostRepo(uow.session)
        user_repo = UserRepo(uow.session)
        service = PostService(post_repo, user_repo=user_repo)
        post = await service.get_post_by_post_url(username, post_slug)
        return give_domain(str(request.base_url), post)
