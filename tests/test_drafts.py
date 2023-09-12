import random
import string
import uuid


def random_string():
    return "".join(random.choices(string.ascii_lowercase, k=1))


def test_create_post(client, headers, payload):
    # not authenticated
    response = client.post("/drafts", json=payload)
    assert response.status_code == 401

    response = client.post("/drafts", json=payload, headers=headers)
    assert response.status_code == 201, response.text
    post_data = response.json()
    assert post_data["title"] == payload["title"]
    assert post_data["body"] == payload["body"]

    # ensure that it is saved in database
    response = client.get("/drafts", headers=headers)
    data = response.json()[0]
    assert data["title"] == payload["title"]
    assert data["body"] == payload["body"]


def test_get_posts(client, headers, payload, headers2):
    # not authenticated
    response = client.get("/drafts")
    assert response.status_code == 401, response.text

    response = client.get("/drafts", headers=headers)
    assert response.status_code == 200, response.text
    assert response.json() == []

    client.post("/drafts", json={"title": "a", "body": "b"}, headers=headers2)
    assert len(client.get("/drafts", headers=headers2).json()) == 1
    assert len(client.get("/drafts", headers=headers).json()) == 0

    test_posts = [
        [{"title": random_string(), "body": random_string()} for _ in range(5)]
        for _ in range(5)
    ]

    posts = [
        client.post("/drafts", json=post, headers=headers).json()
        for post_list in test_posts
        for post in post_list
    ]

    # default query params: page = 1, per-page = 5, sort = date, desc = true
    # pages
    response = client.get("/drafts", headers=headers)
    assert len(response.json()) == 5

    response = client.get("/drafts", params={"page": 2}, headers=headers)
    assert len(response.json()) == 5

    response = client.get("/drafts", params={"page": 3}, headers=headers)
    assert len(response.json()) == 5

    response = client.get("/drafts", params={"page": 4}, headers=headers)
    assert len(response.json()) == 5

    response = client.get("/drafts", params={"page": 5}, headers=headers)
    assert len(response.json()) == 5

    # per-page
    response = client.get("/drafts", params={"per-page": 10}, headers=headers)
    assert len(response.json()) == 10

    response = client.get("/drafts", params={"per-page": 20}, headers=headers)
    assert len(response.json()) == 20

    response = client.get("/drafts", params={"per-page": len(posts)}, headers=headers)
    assert len(response.json()) == len(posts)

    # sort
    response = client.get("/drafts", params={"per-page": len(posts)}, headers=headers)
    assert response.json() == posts[::-1]

    response = client.get(
        "/drafts",
        params={"per-page": len(posts), "sort": "title"},
        headers=headers,
    )
    assert response.json() == sorted(posts, key=lambda x: x["title"], reverse=True)

    # desc
    response = client.get(
        "/drafts",
        params={"per-page": len(posts), "desc": "false"},
        headers=headers,
    )
    assert response.json() == posts


def test_get_post(client, headers, payload):
    response = client.post("/drafts", json=payload)
    assert response.status_code == 401, response.text

    post_id = client.post("/drafts", json=payload, headers=headers).json()["id"]

    response = client.get(f"/drafts/{post_id}", headers=headers)
    assert response.status_code == 200, response.text

    data = response.json()
    assert data["title"] == payload["title"]
    assert data["body"] == payload["body"]


def test_update_post(client, headers, payload):
    new_title, new_body = "a", "b"
    response = client.post("/drafts", json=payload)
    assert response.status_code == 401, response.text

    post_id = client.post("/drafts", json=payload, headers=headers).json()["id"]

    response = client.put(
        f"/drafts/{post_id}",
        json={"title": new_title, "body": new_body},
        headers=headers,
    )
    assert response.status_code == 200, response.text

    data = response.json()
    assert data["title"] == new_title
    assert data["body"] == new_body


def test_delete_post(client, headers, payload):
    response = client.post("/drafts", json=payload)
    assert response.status_code == 401, response.text

    post_id = client.post("/drafts", json=payload, headers=headers).json()["id"]

    response = client.delete(f"/drafts/{post_id}", headers=headers)
    assert response.status_code == 204, response.text
    assert client.get(f"/posts{post_id}").status_code == 404


def test_get_post_fail(client, headers):
    post_id = uuid.uuid4()
    response = client.get(f"/drafts/{post_id}", headers=headers)
    assert response.status_code == 404, response.text


def test_update_post_fail(client, headers):
    post_id = uuid.uuid4()
    response = client.put(
        f"/drafts/{post_id}",
        json={"title": "a", "body": "b"},
        headers=headers,
    )
    assert response.status_code == 404, response.text


def test_delete_post_fail(client, headers):
    post_id = uuid.uuid4()
    response = client.delete(f"/drafts/{post_id}", headers=headers)
    assert response.status_code == 404, response.text
