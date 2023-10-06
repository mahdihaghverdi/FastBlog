import asyncio
import pathlib
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


@pytest.fixture(scope="session")
def payload():
    return {"title": title, "body": body, "tags": ["1"]}


@pytest.fixture(scope="session")
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


# class level fixtures for comments tests #
class BaseTest:
    @staticmethod
    def assert_details(got, had):
        assert got["comment"] == had["comment"]
        assert got["parent_id"] == had["parent_id"]
        assert got["path"] == had["path"]
        assert got["username"] == had["username"]


@pytest.fixture(scope="class")
def class_client() -> TestClient:
    try:
        yield TestClient(app=app)
    finally:
        asyncio.run(drop_all())


@pytest.fixture(scope="class")
def class_headers(class_client, username="string", password="password"):
    class_client.post(
        "/users/signup",
        data={"username": username, "password": password},
    )
    access_token = class_client.post(
        "/auth/access-token",
        data={"grant_type": "password", "username": username, "password": password},
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    return headers


@pytest.fixture(scope="class")
def post_id_comments(class_client, class_headers, payload):
    post_id = class_client.post("/posts", headers=class_headers, json=payload).json()[
        "id"
    ]
    c1 = class_client.post(
        f"/posts/{post_id}/comment",
        headers=class_headers,
        json="my comment 1",
    ).json()
    c2 = class_client.post(
        f"/posts/{post_id}/comment",
        headers=class_headers,
        json="my comment 2",
    ).json()
    c3 = class_client.post(
        f"/posts/{post_id}/comment",
        headers=class_headers,
        json="my comment 3",
    ).json()
    c4 = class_client.post(
        f"/posts/{post_id}/comment",
        headers=class_headers,
        json="my comment 4",
    ).json()
    c5 = class_client.post(
        f"/posts/{post_id}/comment",
        headers=class_headers,
        json="my comment 5",
    ).json()

    return post_id, [c1, c2, c3, c4, c5]


@pytest.fixture(scope="class")
def post_id_comments_replies(class_client, class_headers, payload):
    post_id = class_client.post("/posts", headers=class_headers, json=payload).json()[
        "id"
    ]
    c1 = class_client.post(
        f"/posts/{post_id}/comment",
        headers=class_headers,
        json="my comment 1",
    ).json()
    r1 = class_client.post(
        f"/posts/{post_id}/comment/{c1['id']}",
        headers=class_headers,
        json="my reply 1.1",
    ).json()

    c2 = class_client.post(
        f"/posts/{post_id}/comment",
        headers=class_headers,
        json="my comment 2",
    ).json()
    r2 = class_client.post(
        f"/posts/{post_id}/comment/{c2['id']}",
        headers=class_headers,
        json="my reply 2.1",
    ).json()

    c3 = class_client.post(
        f"/posts/{post_id}/comment",
        headers=class_headers,
        json="my comment 3",
    ).json()
    r3 = class_client.post(
        f"/posts/{post_id}/comment/{c3['id']}",
        headers=class_headers,
        json="my reply 3.1",
    ).json()

    c4 = class_client.post(
        f"/posts/{post_id}/comment",
        headers=class_headers,
        json="my comment 4",
    ).json()
    r4 = class_client.post(
        f"/posts/{post_id}/comment/{c4['id']}",
        headers=class_headers,
        json="my reply 4.1",
    ).json()

    c5 = class_client.post(
        f"/posts/{post_id}/comment",
        headers=class_headers,
        json="my comment 5",
    ).json()
    r5 = class_client.post(
        f"/posts/{post_id}/comment/{c5['id']}",
        headers=class_headers,
        json="my reply 5.1",
    ).json()

    base_comments = [c1, c2, c3, c4, c5]
    replies = [r1, r2, r3, r4, r5]
    comments_and_replies = [c1, r1, c2, r2, c3, r3, c4, r4, c5, r5]
    return post_id, base_comments, replies, comments_and_replies


@pytest.fixture(scope="class")
def post_id_comments_replies_two_level(class_client, class_headers, payload):
    post_id = class_client.post("/posts", headers=class_headers, json=payload).json()[
        "id"
    ]
    c1 = class_client.post(
        f"/posts/{post_id}/comment",
        headers=class_headers,
        json="my comment 1",
    ).json()
    r1 = class_client.post(
        f"/posts/{post_id}/comment/{c1['id']}",
        headers=class_headers,
        json="my reply 1.1",
    ).json()
    r11 = class_client.post(
        f"/posts/{post_id}/comment/{r1['id']}",
        headers=class_headers,
        json="my reply 1.1.1",
    ).json()

    c2 = class_client.post(
        f"/posts/{post_id}/comment",
        headers=class_headers,
        json="my comment 2",
    ).json()
    r2 = class_client.post(
        f"/posts/{post_id}/comment/{c2['id']}",
        headers=class_headers,
        json="my reply 2.1",
    ).json()
    r21 = class_client.post(
        f"/posts/{post_id}/comment/{r2['id']}",
        headers=class_headers,
        json="my reply 2.1.1",
    ).json()

    c3 = class_client.post(
        f"/posts/{post_id}/comment",
        headers=class_headers,
        json="my comment 3",
    ).json()
    r3 = class_client.post(
        f"/posts/{post_id}/comment/{c3['id']}",
        headers=class_headers,
        json="my reply 3.1",
    ).json()
    r31 = class_client.post(
        f"/posts/{post_id}/comment/{r3['id']}",
        headers=class_headers,
        json="my reply 3.1.1",
    ).json()

    c4 = class_client.post(
        f"/posts/{post_id}/comment",
        headers=class_headers,
        json="my comment 4",
    ).json()
    r4 = class_client.post(
        f"/posts/{post_id}/comment/{c4['id']}",
        headers=class_headers,
        json="my reply 4.1",
    ).json()
    r41 = class_client.post(
        f"/posts/{post_id}/comment/{r4['id']}",
        headers=class_headers,
        json="my reply 4.1.1",
    ).json()

    c5 = class_client.post(
        f"/posts/{post_id}/comment",
        headers=class_headers,
        json="my comment 5",
    ).json()
    r5 = class_client.post(
        f"/posts/{post_id}/comment/{c5['id']}",
        headers=class_headers,
        json="my reply 5.1",
    ).json()
    r51 = class_client.post(
        f"/posts/{post_id}/comment/{r5['id']}",
        headers=class_headers,
        json="my reply 5.1.1",
    ).json()

    base_comments = [c1, c2, c3, c4, c5]
    level_one_reply = [r1, r2, r3, r4, r5]
    all_comments = [c1, r1, r11, c2, r2, r21, c3, r3, r31, c4, r4, r41, c5, r5, r51]
    return post_id, base_comments, level_one_reply, all_comments


@pytest.fixture(scope="class")
def post_id_comments_replies_three_level(class_client, class_headers, payload):
    post_id = class_client.post("/posts", headers=class_headers, json=payload).json()[
        "id"
    ]
    c1 = class_client.post(
        f"/posts/{post_id}/comment",
        headers=class_headers,
        json="my comment 1",
    ).json()
    r1 = class_client.post(
        f"/posts/{post_id}/comment/{c1['id']}",
        headers=class_headers,
        json="my reply 1.1",
    ).json()
    r11 = class_client.post(
        f"/posts/{post_id}/comment/{r1['id']}",
        headers=class_headers,
        json="my reply 1.1.1",
    ).json()
    r111 = class_client.post(
        f"/posts/{post_id}/comment/{r11['id']}",
        headers=class_headers,
        json="my reply 1.1.1.1",
    ).json()

    c2 = class_client.post(
        f"/posts/{post_id}/comment",
        headers=class_headers,
        json="my comment 2",
    ).json()
    r2 = class_client.post(
        f"/posts/{post_id}/comment/{c2['id']}",
        headers=class_headers,
        json="my reply 2.1",
    ).json()
    r21 = class_client.post(
        f"/posts/{post_id}/comment/{r2['id']}",
        headers=class_headers,
        json="my reply 2.1.1",
    ).json()
    r211 = class_client.post(
        f"/posts/{post_id}/comment/{r21['id']}",
        headers=class_headers,
        json="my reply 2.1.1.1",
    ).json()

    c3 = class_client.post(
        f"/posts/{post_id}/comment",
        headers=class_headers,
        json="my comment 3",
    ).json()
    r3 = class_client.post(
        f"/posts/{post_id}/comment/{c3['id']}",
        headers=class_headers,
        json="my reply 3.1",
    ).json()
    r31 = class_client.post(
        f"/posts/{post_id}/comment/{r3['id']}",
        headers=class_headers,
        json="my reply 3.1.1",
    ).json()
    r311 = class_client.post(
        f"/posts/{post_id}/comment/{r31['id']}",
        headers=class_headers,
        json="my reply 3.1.1.1",
    ).json()

    c4 = class_client.post(
        f"/posts/{post_id}/comment",
        headers=class_headers,
        json="my comment 4",
    ).json()
    r4 = class_client.post(
        f"/posts/{post_id}/comment/{c4['id']}",
        headers=class_headers,
        json="my reply 4.1",
    ).json()
    r41 = class_client.post(
        f"/posts/{post_id}/comment/{r4['id']}",
        headers=class_headers,
        json="my reply 4.1.1",
    ).json()
    r411 = class_client.post(
        f"/posts/{post_id}/comment/{r41['id']}",
        headers=class_headers,
        json="my reply 4.1.1.1",
    ).json()

    c5 = class_client.post(
        f"/posts/{post_id}/comment",
        headers=class_headers,
        json="my comment 5",
    ).json()
    r5 = class_client.post(
        f"/posts/{post_id}/comment/{c5['id']}",
        headers=class_headers,
        json="my reply 5.1",
    ).json()
    r51 = class_client.post(
        f"/posts/{post_id}/comment/{r5['id']}",
        headers=class_headers,
        json="my reply 5.1.1",
    ).json()
    r511 = class_client.post(
        f"/posts/{post_id}/comment/{r51['id']}",
        headers=class_headers,
        json="my reply 5.1.1.1",
    ).json()

    base_comments = [c1, c2, c3, c4, c5]
    level_one_reply = [r1, r2, r3, r4, r5]
    level_two_reply = [r11, r21, r31, r41, r51]
    level_three_reply = [r111, r211, r311, r411, r511]

    all_comments = [
        c1,
        r1,
        r11,
        r111,
        c2,
        r2,
        r21,
        r211,
        c3,
        r3,
        r31,
        r311,
        c4,
        r4,
        r41,
        r411,
        c5,
        r5,
        r51,
        r511,
    ]
    return (
        post_id,
        base_comments,
        level_one_reply,
        level_two_reply,
        level_three_reply,
        all_comments,
    )


# Reply tests
@pytest.fixture(scope="class")
def post_id_comment_id_replies(class_client, class_headers, payload):
    post_id = class_client.post("/posts", headers=class_headers, json=payload).json()[
        "id"
    ]
    comment_id = class_client.post(
        f"/posts/{post_id}/comment",
        headers=class_headers,
        json="my comment 1",
    ).json()["id"]
    r1 = class_client.post(
        f"/posts/{post_id}/comment/{comment_id}",
        headers=class_headers,
        json="my reply 1.1",
    ).json()
    r2 = class_client.post(
        f"/posts/{post_id}/comment/{comment_id}",
        headers=class_headers,
        json="my reply 1.2",
    ).json()
    r3 = class_client.post(
        f"/posts/{post_id}/comment/{comment_id}",
        headers=class_headers,
        json="my reply 1.3",
    ).json()
    r4 = class_client.post(
        f"/posts/{post_id}/comment/{comment_id}",
        headers=class_headers,
        json="my reply 1.4",
    ).json()
    r5 = class_client.post(
        f"/posts/{post_id}/comment/{comment_id}",
        headers=class_headers,
        json="my reply 1.5",
    ).json()

    replies = [r1, r2, r3, r4, r5]
    return post_id, comment_id, replies


@pytest.fixture(scope="class")
def post_id_comment_id_replies_one_level(class_client, class_headers, payload):
    post_id = class_client.post("/posts", headers=class_headers, json=payload).json()[
        "id"
    ]
    comment_id = class_client.post(
        f"/posts/{post_id}/comment",
        headers=class_headers,
        json="my comment 1",
    ).json()["id"]

    r1 = class_client.post(
        f"/posts/{post_id}/comment/{comment_id}",
        headers=class_headers,
        json="my reply 1.1",
    ).json()
    r11 = class_client.post(
        f"/posts/{post_id}/comment/{r1['id']}",
        headers=class_headers,
        json="my reply 1.1.1",
    ).json()

    r2 = class_client.post(
        f"/posts/{post_id}/comment/{comment_id}",
        headers=class_headers,
        json="my reply 1.2",
    ).json()
    r21 = class_client.post(
        f"/posts/{post_id}/comment/{r2['id']}",
        headers=class_headers,
        json="my reply 1.2.1",
    ).json()

    r3 = class_client.post(
        f"/posts/{post_id}/comment/{comment_id}",
        headers=class_headers,
        json="my reply 1.3",
    ).json()
    r31 = class_client.post(
        f"/posts/{post_id}/comment/{r3['id']}",
        headers=class_headers,
        json="my reply 1.3.1",
    ).json()

    r4 = class_client.post(
        f"/posts/{post_id}/comment/{comment_id}",
        headers=class_headers,
        json="my reply 1.4",
    ).json()
    r41 = class_client.post(
        f"/posts/{post_id}/comment/{r4['id']}",
        headers=class_headers,
        json="my reply 1.4.1",
    ).json()

    r5 = class_client.post(
        f"/posts/{post_id}/comment/{comment_id}",
        headers=class_headers,
        json="my reply 1.5",
    ).json()
    r51 = class_client.post(
        f"/posts/{post_id}/comment/{r5['id']}",
        headers=class_headers,
        json="my reply 1.5.1",
    ).json()

    return (
        post_id,
        comment_id,
        [r1, r2, r3, r4, r5],
        [r1, r11, r2, r21, r3, r31, r4, r41, r5, r51],
    )


@pytest.fixture(scope="class")
def post_id_comment_id_replies_two_level(class_client, class_headers, payload):
    post_id = class_client.post("/posts", headers=class_headers, json=payload).json()[
        "id"
    ]
    comment_id = class_client.post(
        f"/posts/{post_id}/comment",
        headers=class_headers,
        json="my comment 1",
    ).json()["id"]

    r1 = class_client.post(
        f"/posts/{post_id}/comment/{comment_id}",
        headers=class_headers,
        json="my reply 1.1",
    ).json()
    r11 = class_client.post(
        f"/posts/{post_id}/comment/{r1['id']}",
        headers=class_headers,
        json="my reply 1.1.1",
    ).json()
    r111 = class_client.post(
        f'/posts/{post_id}/comment/{r11["id"]}',
        headers=class_headers,
        json="my reply 1.1.1.1",
    ).json()

    r2 = class_client.post(
        f"/posts/{post_id}/comment/{comment_id}",
        headers=class_headers,
        json="my reply 1.2",
    ).json()
    r21 = class_client.post(
        f"/posts/{post_id}/comment/{r2['id']}",
        headers=class_headers,
        json="my reply 1.2.1",
    ).json()
    r211 = class_client.post(
        f'/posts/{post_id}/comment/{r21["id"]}',
        headers=class_headers,
        json="my reply 1.2.1.1",
    ).json()

    r3 = class_client.post(
        f"/posts/{post_id}/comment/{comment_id}",
        headers=class_headers,
        json="my reply 1.3",
    ).json()
    r31 = class_client.post(
        f"/posts/{post_id}/comment/{r3['id']}",
        headers=class_headers,
        json="my reply 1.3.1",
    ).json()
    r311 = class_client.post(
        f'/posts/{post_id}/comment/{r31["id"]}',
        headers=class_headers,
        json="my reply 1.3.1.1",
    ).json()

    r4 = class_client.post(
        f"/posts/{post_id}/comment/{comment_id}",
        headers=class_headers,
        json="my reply 1.4",
    ).json()
    r41 = class_client.post(
        f"/posts/{post_id}/comment/{r4['id']}",
        headers=class_headers,
        json="my reply 1.4.1",
    ).json()
    r411 = class_client.post(
        f'/posts/{post_id}/comment/{r41["id"]}',
        headers=class_headers,
        json="my reply 1.4.1.1",
    ).json()

    r5 = class_client.post(
        f"/posts/{post_id}/comment/{comment_id}",
        headers=class_headers,
        json="my reply 1.5",
    ).json()
    r51 = class_client.post(
        f"/posts/{post_id}/comment/{r5['id']}",
        headers=class_headers,
        json="my reply 1.5.1",
    ).json()
    r511 = class_client.post(
        f'/posts/{post_id}/comment/{r51["id"]}',
        headers=class_headers,
        json="my reply 1.5.1.1",
    ).json()

    base_replies = [r1, r2, r3, r4, r5]
    level_one_reply = [r11, r21, r31, r41, r51]
    all_replies = [
        r1,
        r11,
        r111,
        r2,
        r21,
        r211,
        r3,
        r31,
        r311,
        r4,
        r41,
        r411,
        r5,
        r51,
        r511,
    ]
    return post_id, comment_id, base_replies, level_one_reply, all_replies


@pytest.fixture(scope="class")
def post_id_comment_id_replies_three_level(class_client, class_headers, payload):
    post_id = class_client.post("/posts", headers=class_headers, json=payload).json()[
        "id"
    ]
    comment_id = class_client.post(
        f"/posts/{post_id}/comment",
        headers=class_headers,
        json="my comment 1",
    ).json()["id"]
    r1 = class_client.post(
        f"/posts/{post_id}/comment/{comment_id}",
        headers=class_headers,
        json="my reply 1.1",
    ).json()
    r11 = class_client.post(
        f"/posts/{post_id}/comment/{r1['id']}",
        headers=class_headers,
        json="my reply 1.1.1",
    ).json()
    r111 = class_client.post(
        f'/posts/{post_id}/comment/{r11["id"]}',
        headers=class_headers,
        json="my reply 1.1.1.1",
    ).json()
    r1111 = class_client.post(
        f'/posts/{post_id}/comment/{r111["id"]}',
        headers=class_headers,
        json="my reply 1.1.1.1.1",
    ).json()

    r2 = class_client.post(
        f"/posts/{post_id}/comment/{comment_id}",
        headers=class_headers,
        json="my reply 1.2",
    ).json()
    r21 = class_client.post(
        f"/posts/{post_id}/comment/{r2['id']}",
        headers=class_headers,
        json="my reply 1.2.1",
    ).json()
    r211 = class_client.post(
        f'/posts/{post_id}/comment/{r21["id"]}',
        headers=class_headers,
        json="my reply 1.2.1.1",
    ).json()
    r2111 = class_client.post(
        f'/posts/{post_id}/comment/{r211["id"]}',
        headers=class_headers,
        json="my reply 1.2.1.1.1",
    ).json()

    r3 = class_client.post(
        f"/posts/{post_id}/comment/{comment_id}",
        headers=class_headers,
        json="my reply 1.3",
    ).json()
    r31 = class_client.post(
        f"/posts/{post_id}/comment/{r3['id']}",
        headers=class_headers,
        json="my reply 1.3.1",
    ).json()
    r311 = class_client.post(
        f'/posts/{post_id}/comment/{r31["id"]}',
        headers=class_headers,
        json="my reply 1.3.1.1",
    ).json()
    r3111 = class_client.post(
        f'/posts/{post_id}/comment/{r311["id"]}',
        headers=class_headers,
        json="my reply 1.3.1.1.1",
    ).json()

    r4 = class_client.post(
        f"/posts/{post_id}/comment/{comment_id}",
        headers=class_headers,
        json="my reply 1.4",
    ).json()
    r41 = class_client.post(
        f"/posts/{post_id}/comment/{r4['id']}",
        headers=class_headers,
        json="my reply 1.4.1",
    ).json()
    r411 = class_client.post(
        f'/posts/{post_id}/comment/{r41["id"]}',
        headers=class_headers,
        json="my reply 1.4.1.1",
    ).json()
    r4111 = class_client.post(
        f'/posts/{post_id}/comment/{r411["id"]}',
        headers=class_headers,
        json="my reply 1.4.1.1.1",
    ).json()

    r5 = class_client.post(
        f"/posts/{post_id}/comment/{comment_id}",
        headers=class_headers,
        json="my reply 1.5",
    ).json()
    r51 = class_client.post(
        f"/posts/{post_id}/comment/{r5['id']}",
        headers=class_headers,
        json="my reply 1.5.1",
    ).json()
    r511 = class_client.post(
        f'/posts/{post_id}/comment/{r51["id"]}',
        headers=class_headers,
        json="my reply 1.5.1.1",
    ).json()
    r5111 = class_client.post(
        f'/posts/{post_id}/comment/{r511["id"]}',
        headers=class_headers,
        json="my reply 1.5.1.1.1",
    ).json()

    base_replies = [r1, r2, r3, r4, r5]
    level_one_reply = [r11, r21, r31, r41, r51]
    level_two_reply = [r111, r211, r311, r411, r511]
    all_replies = [
        r1,
        r11,
        r111,
        r1111,
        r2,
        r21,
        r211,
        r2111,
        r3,
        r31,
        r311,
        r3111,
        r4,
        r41,
        r411,
        r4111,
        r5,
        r51,
        r511,
        r5111,
    ]
    return (
        post_id,
        comment_id,
        base_replies,
        level_one_reply,
        level_two_reply,
        all_replies,
    )
