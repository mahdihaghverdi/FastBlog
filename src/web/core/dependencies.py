from collections import namedtuple
from typing import Annotated

from fastapi import Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError  # noqa
from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession
from starlette import status

from src.repository.repos.user_repo import UserRepo
from src.repository.unit_of_work import UnitOfWork
from src.service.user_service import UserService
from src.web.core.config import settings
from src.web.core.database import sqlalchemy_engine
from src.web.core.schemas import Sort


async def get_async_sessionmaker() -> async_sessionmaker:
    return async_sessionmaker(sqlalchemy_engine, expire_on_commit=False)


async def get_db(
    asessionmaker: Annotated[async_sessionmaker, Depends(get_async_sessionmaker)],
) -> AsyncSession:
    db = asessionmaker()
    try:
        yield db
    finally:
        await db.close()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/access-token")

QueryParameters = namedtuple("QueryParameters", "page per_page sort desc")


async def returning_query_parameters(
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
    return QueryParameters(page, per_page, sort, desc)


async def get_user(
    session: Annotated[AsyncSession, Depends(get_db)],
    user_id,
    full=False,
):
    async with UnitOfWork(session) as uow:
        repo = UserRepo(uow.session)
        service = UserService(repo)
        return await service.get_user(user_id, full)


async def get_current_user_simple(
    session: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[str, Depends(oauth2_scheme)],
):
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
    user = await get_user(session, int(user_id))
    return user


async def get_current_user_full(
    session: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[str, Depends(oauth2_scheme)],
):
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
    user = await get_user(session, int(user_id), full=True)
    return user
