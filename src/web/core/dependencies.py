from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError  # noqa
from sqlalchemy.ext.asyncio import async_sessionmaker

from src.web.core.database import sqlalchemy_engine


async def get_async_sessionmaker() -> async_sessionmaker:
    return async_sessionmaker(sqlalchemy_engine, expire_on_commit=False)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="access-token")
