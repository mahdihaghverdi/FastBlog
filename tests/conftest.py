import asyncio
import pathlib
import random
import string
import sys

import pytest
from sqlalchemy import NullPool
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from starlette.testclient import TestClient

sys.path.append(str(pathlib.Path(__file__).parent.parent))
from src.repository.models import Base  # noqa: E402
from src.web.app import app  # noqa: E402
from src.web.core.config import settings  # noqa: E402
from src.web.core.dependencies import get_async_sessionmaker  # noqa: E402


def random_string():
    return "".join(random.choices(string.ascii_lowercase, k=1))


test_posts = [
    [
        {"title": random_string(), "body": random_string(), "tags": ["a"]}
        for _ in range(5)
    ]
    for _ in range(5)
]


async def get_async_sessionmaker_mock():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    return async_sessionmaker(
        engine,
        expire_on_commit=False,
        autocommit=False,
        autoflush=False,
    )


app.dependency_overrides[get_async_sessionmaker] = get_async_sessionmaker_mock


@pytest.fixture(scope="function")
def headers(client, username="string", password="password"):
    client.post("/users/signup", data={"username": username, "password": password})
    access_token = client.post(
        "/auth/access-token",
        data={"grant_type": "password", "username": username, "password": password},
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    return headers


@pytest.fixture(scope="function")
def headers2(client, username="mahdi", password="password"):
    client.post("/users/signup", data={"username": username, "password": password})
    access_token = client.post(
        "/auth/access-token",
        data={"grant_type": "password", "username": username, "password": password},
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    return headers


title = "Python 3.11"
body = "Wow, such a release!"
new_title = "the Ugly umbrella"


@pytest.fixture(scope="function")
def payload():
    return {"title": title, "body": body, "tags": ["1"]}


@pytest.fixture(scope="function")
def payload2():
    return {"title": title, "body": body, "title_in_url": new_title, "tags": [1]}


engine = create_async_engine(str(settings.database_url), poolclass=NullPool)


async def drop_all():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
def client() -> TestClient:
    try:
        yield TestClient(app=app)
    finally:
        asyncio.run(drop_all())
