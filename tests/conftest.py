import asyncio
import pathlib
import sys

import pytest
from slugify import Slugify
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

s = Slugify(to_lower=True)
_title_slug = s(title)
_new_slug = s(new_title)


@pytest.fixture(scope="function")
def payload():
    return {"title": title, "body": body, "title_in_url": None}


@pytest.fixture(scope="function")
def title_slug():
    return _title_slug


@pytest.fixture(scope="function")
def new_slug():
    return _new_slug


@pytest.fixture(scope="function")
def payload2():
    return {"title": title, "body": body, "title_in_url": new_title}


@pytest.fixture(scope="function")
def client() -> TestClient:
    asyncio.run(create_all())
    try:
        yield TestClient(app=app)
    finally:
        asyncio.run(drop_all())
