from typing import Annotated

from fastapi import APIRouter, Depends, Form
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.requests import Request

from src.repository.repos.user_repo import UserRepo
from src.repository.unit_of_work import UnitOfWork
from src.service.user_service import UserService
from src.web.api import give_domain
from src.web.core.dependencies import get_db, get_current_user_full
from src.web.core.schemas import UserOutSchema, UserSignUpSchema, UserInternalSchema

router = APIRouter(prefix="/users", tags=["users"])


@router.post(
    "/signup",
    response_model=UserOutSchema,
    status_code=status.HTTP_201_CREATED,
)
async def signup_user(
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    session: Annotated[AsyncSession, Depends(get_db)],
):
    async with UnitOfWork(session) as uow:
        repo = UserRepo(uow.session)
        service = UserService(repo)
        user = await service.create_user(
            UserSignUpSchema(username=username, password=password).model_dump(),
        )
        await uow.commit()
        return user


@router.get("/me", response_model=UserOutSchema)
async def read_users_me(
    request: Request,
    current_user: Annotated[UserInternalSchema, Depends(get_current_user_full)],
):
    current_user["posts"] = give_domain(str(request.base_url), current_user["posts"])
    return current_user
