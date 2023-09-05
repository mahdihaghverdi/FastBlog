from functools import lru_cache

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.web.config import Settings


@lru_cache
def get_settings() -> Settings:
    return Settings()


sqlalchemy_engine = create_async_engine(str(get_settings().database_url))


def get_async_sessionmaker() -> async_sessionmaker:
    return async_sessionmaker(sqlalchemy_engine, expire_on_commit=False)
