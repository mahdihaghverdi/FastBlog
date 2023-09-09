import asyncio
import pathlib
import sys

import pytest
from starlette.testclient import TestClient

sys.path.append(str(pathlib.Path(__file__).parent.parent))
from src.repository.models import Base  # noqa: E402
from src.web.app import app  # noqa: E402
from src.web.core.database import sqlalchemy_engine as engine  # noqa: E402


async def create_all():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_all():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
def client() -> TestClient:
    asyncio.run(create_all())
    try:
        yield TestClient(app=app)
    finally:
        asyncio.run(drop_all())
