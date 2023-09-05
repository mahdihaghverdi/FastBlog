import random
import string


def test_create_post(client):
    title, body = "Python 3.11", "Wow, such a release!"
    response = client.post(
        "/posts",
        json={
            "title": title,
            "body": body,
        },
    )
    assert response.status_code == 201, response.text

    post_data = response.json()
    assert post_data["title"] == title
    assert post_data["body"] == body

    response = client.get("/posts")
    assert response.status_code == 200, response.text

    post = response.json()[0]
    assert post["id"] == post_data["id"]
    assert post["created"] == post_data["created"]
    assert post["title"] == post_data["title"]
    assert post["body"] == post_data["body"]


def random_string():
    return "".join(random.choices(string.ascii_lowercase, k=1))


def test_get_posts(client):
    response = client.get("/posts")
    assert response.status_code == 200, response.text
    assert response.json() == []

    posts = [
        [{"title": random_string(), "body": random_string()} for _ in range(5)]
        for _ in range(5)
    ]
    posts = [
        client.post("/posts", json=post).json()
        for post_list in posts
        for post in post_list
    ]

    # default query params: page = 1, per-page = 5, sort = date, desc = true
    # pages
    response = client.get("/posts")
    assert len(response.json()) == 5

    response = client.get("/posts", params={"page": 2})
    assert len(response.json()) == 5

    response = client.get("/posts", params={"page": 3})
    assert len(response.json()) == 5

    response = client.get("/posts", params={"page": 4})
    assert len(response.json()) == 5

    response = client.get("/posts", params={"page": 5})
    assert len(response.json()) == 5

    # per-page
    response = client.get("/posts", params={"per-page": 10})
    assert len(response.json()) == 10

    response = client.get("/posts", params={"per-page": 20})
    assert len(response.json()) == 20

    response = client.get("/posts", params={"per-page": len(posts)})
    assert len(response.json()) == len(posts)

    # sort
    response = client.get("/posts", params={"per-page": len(posts)})
    assert response.json() == posts[::-1]

    response = client.get("/posts", params={"per-page": len(posts), "sort": "title"})
    assert response.json() == sorted(posts, key=lambda x: x["title"], reverse=True)

    # desc
    response = client.get("/posts", params={"per-page": len(posts), "desc": "false"})
    assert response.json() == posts


def test_get_post(client):
    title, body = "a", "b"
    post_id = client.post("/posts", json={"title": title, "body": body}).json()["id"]

    response = client.get(f"/posts/{post_id}")
    assert response.status_code == 200, response.text

    data = response.json()
    assert data["title"] == title
    assert data["body"] == body


def test_update_post(client):
    title, body, new_title, new_body = "a", "b", "b", "a"
    post_id = client.post("/posts", json={"title": title, "body": body}).json()["id"]

    response = client.put(
        f"/posts/{post_id}",
        json={"title": new_title, "body": new_body},
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
