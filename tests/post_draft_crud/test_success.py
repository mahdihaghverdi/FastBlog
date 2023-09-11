import random
import string

import pytest

from tests.conftest import signup_and_auth


def random_string():
    return "".join(random.choices(string.ascii_lowercase, k=1))


@pytest.mark.parametrize("endpoint", ["/posts", "drafts"])
def test_create_post(client, endpoint):
    payload = {
        "title": "Python 3.11",
        "body": "Wow, such a release!",
    }

    # not authenticated
    response = client.post(endpoint, json=payload)
    assert response.status_code == 401

    # authenticate and create a post
    headers = signup_and_auth(client)

    response = client.post(endpoint, json=payload, headers=headers)
    assert response.status_code == 201, response.text
    post_data = response.json()
    assert post_data["title"] == payload["title"]
    assert post_data["body"] == payload["body"]

    # ensure that it is saved in database
    response = client.get(endpoint, headers=headers)
    data = response.json()[0]
    assert data["title"] == payload["title"]
    assert data["body"] == payload["body"]


@pytest.mark.parametrize("endpoint", ["/posts", "/drafts"])
def test_get_posts(client, endpoint):
    # not authenticated
    response = client.get(endpoint)
    assert response.status_code == 401, response.text

    # authenticated
    headers = signup_and_auth(client)
    response = client.get(endpoint, headers=headers)
    assert response.status_code == 200, response.text
    assert response.json() == []

    # two signups to see the first is empty
    second = signup_and_auth(client, username="second")
    client.post(endpoint, json={"title": "a", "body": "b"}, headers=second)
    assert len(client.get(endpoint, headers=second).json()) == 1
    assert len(client.get(endpoint, headers=headers).json()) == 0

    test_posts = [
        [{"title": random_string(), "body": random_string()} for _ in range(5)]
        for _ in range(5)
    ]

    posts = [
        client.post(endpoint, json=post, headers=headers).json()
        for post_list in test_posts
        for post in post_list
    ]

    # default query params: page = 1, per-page = 5, sort = date, desc = true
    # pages
    response = client.get(endpoint, headers=headers)
    assert len(response.json()) == 5

    response = client.get(endpoint, params={"page": 2}, headers=headers)
    assert len(response.json()) == 5

    response = client.get(endpoint, params={"page": 3}, headers=headers)
    assert len(response.json()) == 5

    response = client.get(endpoint, params={"page": 4}, headers=headers)
    assert len(response.json()) == 5

    response = client.get(endpoint, params={"page": 5}, headers=headers)
    assert len(response.json()) == 5

    # per-page
    response = client.get(endpoint, params={"per-page": 10}, headers=headers)
    assert len(response.json()) == 10

    response = client.get(endpoint, params={"per-page": 20}, headers=headers)
    assert len(response.json()) == 20

    response = client.get(endpoint, params={"per-page": len(posts)}, headers=headers)
    assert len(response.json()) == len(posts)

    # sort
    response = client.get(endpoint, params={"per-page": len(posts)}, headers=headers)
    assert response.json() == posts[::-1]

    response = client.get(
        endpoint,
        params={"per-page": len(posts), "sort": "title"},
        headers=headers,
    )
    assert response.json() == sorted(posts, key=lambda x: x["title"], reverse=True)

    # desc
    response = client.get(
        endpoint,
        params={"per-page": len(posts), "desc": "false"},
        headers=headers,
    )
    assert response.json() == posts


@pytest.mark.parametrize("endpoint", ["/posts", "/drafts"])
def test_get_post(client, endpoint):
    title, body = "a", "b"
    response = client.post(endpoint, json={"title": title, "body": body})
    assert response.status_code == 401, response.text

    headers = signup_and_auth(client)
    post_id = client.post(
        endpoint,
        json={"title": title, "body": body},
        headers=headers,
    ).json()["id"]

    response = client.get(f"{endpoint}/{post_id}", headers=headers)
    assert response.status_code == 200, response.text

    data = response.json()
    assert data["title"] == title
    assert data["body"] == body


@pytest.mark.parametrize("endpoint", ["/posts", "/drafts"])
def test_update_post(client, endpoint):
    title, body, new_title, new_body = "a", "b", "b", "a"
    response = client.post(endpoint, json={"title": title, "body": body})
    assert response.status_code == 401, response.text

    headers = signup_and_auth(client)
    post_id = client.post(
        endpoint,
        json={"title": title, "body": body},
        headers=headers,
    ).json()["id"]

    response = client.put(
        f"{endpoint}/{post_id}",
        json={"title": new_title, "body": new_body},
        headers=headers,
    )
    assert response.status_code == 200, response.text

    data = response.json()
    assert data["title"] == new_title
    assert data["body"] == new_body


@pytest.mark.parametrize("endpoint", ["/posts", "/drafts"])
def test_delete_post(client, endpoint):
    title, body = "a", "b"
    response = client.post(endpoint, json={"title": title, "body": body})
    assert response.status_code == 401, response.text

    headers = signup_and_auth(client)
    post_id = client.post(
        endpoint,
        json={"title": title, "body": body},
        headers=headers,
    ).json()["id"]

    response = client.delete(f"{endpoint}/{post_id}", headers=headers)
    assert response.status_code == 204, response.text
    assert client.get(f"/posts{post_id}").status_code == 404
