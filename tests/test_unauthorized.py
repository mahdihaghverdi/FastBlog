def test_not_authorized_drafts(client, headers, payload):
    response = client.post("/drafts", json=payload)
    assert response.status_code == 401, response.text

    draft_id = client.post("/drafts", json=payload, headers=headers).json()["id"]

    response = client.get("/drafts")
    assert response.status_code == 401, response.text

    response = client.get(f"/drafts/{draft_id}")
    assert response.status_code == 401, response.text

    response = client.put(f"/drafts/{draft_id}", json=payload)
    assert response.status_code == 401, response.text

    response = client.delete(f"/drafts/{draft_id}")
    assert response.status_code == 401, response.text


def test_not_authorized_me(client, headers):
    response = client.get("/users/me")
    assert response.status_code == 401, response.text


def test_not_authorized_posts(client, headers, payload):
    response = client.post("/posts", json=payload)
    assert response.status_code == 401, response.text

    post_id = client.post("/posts", json=payload, headers=headers).json()["id"]

    response = client.get("/posts")
    assert response.status_code == 401, response.text

    response = client.get(f"/posts/{post_id}")
    assert response.status_code == 401, response.text

    response = client.put(f"/posts/{post_id}", json=payload)
    assert response.status_code == 401, response.text

    response = client.delete(f"/posts/{post_id}")
    assert response.status_code == 401, response.text
