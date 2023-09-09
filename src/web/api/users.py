from typing import Annotated

from fastapi import APIRouter, Depends, Form
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker
from starlette import status

from src.common.exceptions import DuplicateUsernameError
from src.repository.unit_of_work import UnitOfWork
from src.repository.user_repository import UserRepo
from src.service.user_service import UserService
from src.web.core.schemas import UserSchema, UserSignUpSchema
from src.web.core.dependencies import get_async_sessionmaker, get_current_user

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/signup", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def signup_user(
    username: Annotated[str, Form()],
    password: Annotated[str, Form()],
    asessionmaker: Annotated[async_sessionmaker, Depends(get_async_sessionmaker)],
):
    async with UnitOfWork(asessionmaker) as uow:
        repo = UserRepo(uow.session)
        service = UserService(repo)
        user = await service.create_user(
            UserSignUpSchema(username=username, password=password).model_dump(),
        )
        try:
            await uow.commit()
        except IntegrityError:
            raise DuplicateUsernameError(f"username: {user.username!r} already exists!")
        else:
            return await user.dict()


@router.get("/me", response_model=UserSchema)
async def read_users_me(current_user: Annotated[UserSchema, Depends(get_current_user)]):
    return current_user
