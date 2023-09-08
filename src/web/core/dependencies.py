from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError  # noqa
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.repository.unit_of_work import UnitOfWork
from src.repository.user_repository import UserRepository
from src.service.user_service import UserService
from src.service.users import User
from src.web.core.database import sqlalchemy_engine


async def get_async_sessionmaker() -> async_sessionmaker:
    return async_sessionmaker(sqlalchemy_engine, expire_on_commit=False)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="access-token")


def get_user(
    asession: Annotated[async_sessionmaker, Depends(get_async_sessionmaker)],
    user_id,
) -> User:
    with UnitOfWork(asession) as uow:
        repo = UserRepository(uow.session)
        service = UserService(repo)
        return await service.get_user(user_id)
