from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError  # noqa
from sqlalchemy.ext.asyncio import async_sessionmaker
from starlette import status

from src.repository.unit_of_work import UnitOfWork
from src.repository.user_repo import UserRepo
from src.service.user_service import UserService
from src.service.objects import User
from src.web.core.config import settings
from src.web.core.database import sqlalchemy_engine


async def get_async_sessionmaker() -> async_sessionmaker:
    return async_sessionmaker(sqlalchemy_engine, expire_on_commit=False)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"/auth/{settings.access_token_url}")


async def get_user(
    asession: Annotated[async_sessionmaker, Depends(get_async_sessionmaker)],
    user_id,
) -> User:
    async with UnitOfWork(asession) as uow:
        repo = UserRepo(uow.session)
        service = UserService(repo)
        return await service.get_user(user_id)


async def get_current_user(
    asession: Annotated[async_sessionmaker, Depends(get_async_sessionmaker)],
    token: Annotated[str, Depends(oauth2_scheme)],
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token=token,
            key=settings.secret_key,
            algorithms=[settings.algorithm],
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await get_user(asession, UUID(user_id))
    return user
