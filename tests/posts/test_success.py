import random
import string

from src.web.core.config import settings


def signup_and_auth(client, username="string", password="password"):
    client.post("/users/signup", data={"username": username, "password": password})
    access_token = client.post(
        f"/auth/{settings.access_token_url}",
        data={"grant_type": "password", "username": username, "password": password},
    ).json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}
    return headers


def random_string():
    return "".join(random.choices(string.ascii_lowercase, k=1))


def test_create_post(client):
    payload = {
        "title": "Python 3.11",
        "body": "Wow, such a release!",
    }

    # not authenticated
    response = client.post("/posts", json=payload)
    assert response.status_code == 401

    # authenticate and create a post
    headers = signup_and_auth(client)

    response = client.post("/posts", json=payload, headers=headers)
    assert response.status_code == 201, response.text
    post_data = response.json()
    assert post_data["title"] == payload["title"]
    assert post_data["body"] == payload["body"]

    # ensure that it is saved in database
    response = client.get("/posts", headers=headers)
    data = response.json()[0]
    assert data["title"] == payload["title"]
    assert data["body"] == payload["body"]


def test_get_posts(client):
    # not authenticated
    response = client.get("/posts")
    assert response.status_code == 401, response.text

    # authenticated
    headers = signup_and_auth(client)
    response = client.get("/posts", headers=headers)
    assert response.status_code == 200, response.text
    assert response.json() == []

    # two signups to see the first is empty
    second = signup_and_auth(client, username="second")
    client.post("/posts", json={"title": "a", "body": "b"}, headers=second)
    assert len(client.get("/posts", headers=second).json()) == 1
    assert len(client.get("/posts", headers=headers).json()) == 0

    posts = [
        [{"title": random_string(), "body": random_string()} for _ in range(5)]
        for _ in range(5)
    ]
    posts = [
        client.post("/posts", json=post, headers=headers).json()
        for post_list in posts
        for post in post_list
    ]

    # default query params: page = 1, per-page = 5, sort = date, desc = true
    # pages
    response = client.get("/posts", headers=headers)
    assert len(response.json()) == 5

    response = client.get("/posts", params={"page": 2}, headers=headers)
    assert len(response.json()) == 5

    response = client.get("/posts", params={"page": 3}, headers=headers)
    assert len(response.json()) == 5

    response = client.get("/posts", params={"page": 4}, headers=headers)
    assert len(response.json()) == 5

    response = client.get("/posts", params={"page": 5}, headers=headers)
    assert len(response.json()) == 5

    # per-page
    response = client.get("/posts", params={"per-page": 10}, headers=headers)
    assert len(response.json()) == 10

    response = client.get("/posts", params={"per-page": 20}, headers=headers)
    assert len(response.json()) == 20

    response = client.get("/posts", params={"per-page": len(posts)}, headers=headers)
    assert len(response.json()) == len(posts)

    # sort
    response = client.get("/posts", params={"per-page": len(posts)}, headers=headers)
    assert response.json() == posts[::-1]

    response = client.get(
        "/posts",
        params={"per-page": len(posts), "sort": "title"},
        headers=headers,
    )
    assert response.json() == sorted(posts, key=lambda x: x["title"], reverse=True)

    # desc
    response = client.get(
        "/posts",
        params={"per-page": len(posts), "desc": "false"},
        headers=headers,
    )
    assert response.json() == posts


def test_get_post(client):
    title, body = "a", "b"
    response = client.post("/posts", json={"title": title, "body": body})
    assert response.status_code == 401, response.text

    headers = signup_and_auth(client)
    post_id = client.post(
        "/posts",
        json={"title": title, "body": body},
        headers=headers,
    ).json()["id"]

    response = client.get(f"/posts/{post_id}", headers=headers)
    assert response.status_code == 200, response.text

    data = response.json()
    assert data["title"] == title
    assert data["body"] == body


def test_update_post(client):
    title, body, new_title, new_body = "a", "b", "b", "a"
    response = client.post("/posts", json={"title": title, "body": body})
    assert response.status_code == 401, response.text

    headers = signup_and_auth(client)
    post_id = client.post(
        "/posts",
        json={"title": title, "body": body},
        headers=headers,
    ).json()["id"]

    response = client.put(
        f"/posts/{post_id}",
        json={"title": new_title, "body": new_body},
        headers=headers,
    )
    assert response.status_code == 200, response.text

    data = response.json()
    assert data["title"] == new_title
    assert data["body"] == new_body


def test_delete_post(client):
    title, body = "a", "b"
    post_id = client.post("/posts", json={"title": title, "body": body}).json()["id"]

    response = client.delete(f"/posts/{post_id}")
    assert response.status_code == 204, response.text
    assert client.get(f"/posts{post_id}").status_code == 404
