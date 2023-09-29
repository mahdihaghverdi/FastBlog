from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from src.repository.repos.post_repo import PostRepo
from src.repository.repos.user_repo import UserRepo
from src.repository.unit_of_work import UnitOfWork
from src.service.post_service import PostService
from src.web.api import give_domain
from src.web.core.dependencies import get_db
from src.web.core.schemas import PostSchema

router = APIRouter(tags=["global posts"])


@router.get("/@{username}/{post_slug}", response_model=PostSchema)
async def get_global_post(
    username: str,
    post_slug: str,
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db)],
):
    async with UnitOfWork(session) as uow:
        post_repo = PostRepo(uow.session)
        user_repo = UserRepo(uow.session)
        service = PostService(post_repo, user_repo=user_repo)
        post = await service.get_post_by_post_url(username, post_slug)
        post = give_domain(str(request.base_url), post)
        return post
