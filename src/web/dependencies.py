from sqlalchemy.ext.asyncio import async_sessionmaker

from src.web.database import sqlalchemy_engine


def get_async_sessionmaker() -> async_sessionmaker:
    return async_sessionmaker(sqlalchemy_engine, expire_on_commit=False)
