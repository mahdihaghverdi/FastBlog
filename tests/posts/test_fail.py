import uuid

from . import signup_and_auth


def test_get_post(client):
    post_id = uuid.uuid4()
    headers = signup_and_auth(client)

    response = client.get(f"/posts/{post_id}", headers=headers)
    assert response.status_code == 404, response.text
    assert response.json()["detail"] == f"post with id: '{post_id}' is not found"


def test_update_post(client):
    post_id = uuid.uuid4()
    headers = signup_and_auth(client)

    response = client.put(
        f"/posts/{post_id}",
        json={"title": "a", "body": "b"},
        headers=headers,
    )
    assert response.status_code == 404, response.text
    assert response.json()["detail"] == f"post with id: '{post_id}' is not found"


def test_delete_post(client):
    post_id = uuid.uuid4()
    headers = signup_and_auth(client)

    response = client.delete(f"/posts/{post_id}", headers=headers)
    assert response.status_code == 404, response.text
    assert response.json()["detail"] == f"post with id: '{post_id}' is not found"
