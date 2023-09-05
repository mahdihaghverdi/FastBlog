from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker

from src.web.config import Settings


@lru_cache
def get_settings() -> Settings:
    return Settings()


def get_database_url(settings: Annotated[Settings, Depends(get_settings)]) -> str:
    return str(settings.database_url)


def get_db_engine(url: Annotated[str, Depends(get_database_url)]) -> AsyncEngine:
    return create_async_engine(url)


def get_async_sessionmaker(
    db: Annotated[AsyncEngine, Depends(get_db_engine)],
) -> async_sessionmaker:
    return async_sessionmaker(db, expire_on_commit=False)
