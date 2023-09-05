import asyncio
import pathlib
import sys

import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker
from starlette.testclient import TestClient

sys.path.append(str(pathlib.Path(__file__).parent.parent))
from src.repository.models import Base  # noqa: E402
from src.web.app import app  # noqa: E402
from src.web.dependencies import get_async_sessionmaker  # noqa: E402
from src.web.database import sqlalchemy_engine as engine  # noqa: E402


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
