from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from src.web.config import Settings

settings = Settings()
sqlalchemy_engine = create_async_engine(str(settings.database_url))


def get_async_sessionmaker() -> async_sessionmaker:
    return async_sessionmaker(sqlalchemy_engine, expire_on_commit=False)
