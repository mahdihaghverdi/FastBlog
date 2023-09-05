import asyncio

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from starlette.testclient import TestClient

from src.repository.models import Base
from src.web.app import app
from src.web.config import Settings
from src.web.dependencies import get_async_sessionmaker

settings = Settings()
engine = create_async_engine(str(settings.database_url))


async def create_all():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_all():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


def get_async_sessionmaker_mock():
    testing_session = async_sessionmaker(
        bind=engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )
    return testing_session


@pytest.fixture(scope="function")
def client() -> TestClient:
    asyncio.run(create_all())
    app.dependency_overrides[get_async_sessionmaker] = get_async_sessionmaker_mock
    try:
        yield TestClient(app=app)
    finally:
        asyncio.run(drop_all())
