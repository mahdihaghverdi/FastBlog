import random
import string


def random_string():
    return "".join(random.choices(string.ascii_lowercase, k=1))


def extract(post_data):
    title, body, _url = post_data["title"], post_data["body"], post_data["url"]
    url = _url[: len(_url) - 19]
    return title, body, url


def test_create_post_default_slug(client, headers, payload):
    response = client.post("/posts", json=payload, headers=headers)
    assert response.status_code == 201, response.text
    post_data = response.json()
    title, body, url = extract(post_data)

    assert title == title
    assert body == body

    response = client.get("/posts", headers=headers)
    post_data = response.json()[0]
    title, body, url = extract(post_data)

    assert title == title
    assert body == body


def test_create_post_custom_slug(client, headers, payload2):
    response = client.post("/posts", json=payload2, headers=headers)
    assert response.status_code == 201, response.text
    post_data = response.json()
    title, body, url = extract(post_data)

    assert title == title
    assert body == body

    response = client.get("/posts", headers=headers)
    post_data = response.json()[0]
    title, body, url = extract(post_data)

    assert title == title
    assert body == body


def test_get_posts(client, headers, headers2, payload):
    response = client.get("/posts", headers=headers)
    assert response.status_code == 200, response.text
    assert response.json() == []

    # two signups to see the first is empty
    client.post("/posts", json=payload, headers=headers2)
    assert len(client.get("/posts", headers=headers2).json()) == 1
    assert len(client.get("/posts", headers=headers).json()) == 0

    test_posts = [
        [{"title": random_string(), "body": random_string()} for _ in range(5)]
        for _ in range(5)
    ]

    posts = [
        client.post("/posts", json=post, headers=headers).json()
        for post_list in test_posts
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


def test_get_post(client, headers, payload):
    post_id = client.post("/posts", json=payload, headers=headers).json()["id"]

    response = client.get(f"posts/{post_id}", headers=headers)
    assert response.status_code == 200, response.text

    data = response.json()
    assert data["title"] == payload["title"]
    assert data["body"] == payload["body"]


def test_update_post(client, headers, payload):
    new_title, new_body = "a", "b"

    post_id = client.post("/posts", json=payload, headers=headers).json()["id"]

    response = client.put(
        f"posts/{post_id}",
        json={"title": new_title, "body": new_body},
        headers=headers,
    )
    assert response.status_code == 200, response.text

    data = response.json()
    assert data["title"] == new_title
    assert data["body"] == new_body


def test_delete_post(client, headers, payload):
    post_id = client.post("/posts", json=payload, headers=headers).json()["id"]

    response = client.delete(f"posts/{post_id}", headers=headers)
    assert response.status_code == 204, response.text
    assert client.get(f"/posts{post_id}").status_code == 404


def test_get_post_fail(client, headers):
    response = client.get(f"/posts/{random.randint(0, 1)}", headers=headers)
    assert response.status_code == 404, response.text


def test_update_post_fail(client, headers):
    response = client.put(
        f"/posts/{random.randint(0, 1)}",
        json={"title": "a", "body": "b"},
        headers=headers,
    )
    assert response.status_code == 404, response.text


def test_delete_post_fail(client, headers):
    response = client.delete(f"/posts/{random.randint(0, 1)}", headers=headers)
    assert response.status_code == 404, response.text
