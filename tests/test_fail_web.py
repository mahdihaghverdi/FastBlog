import uuid


def test_get_post(client):
    post_id = uuid.uuid4()
    response = client.get(f"/posts/{post_id}")
    assert response.status_code == 404, response.text
    assert response.json()["detail"] == f"post with id: '{post_id}' is not found"


def test_update_post(client):
    post_id = uuid.uuid4()
    response = client.put(f"/posts/{post_id}", json={"title": "a", "body": "b"})
    assert response.status_code == 404, response.text
    assert response.json()["detail"] == f"post with id: '{post_id}' is not found"


def test_delete_post(client):
    post_id = uuid.uuid4()
    response = client.delete(f"/posts/{post_id}")
    assert response.status_code == 404, response.text
    assert response.json()["detail"] == f"post with id: '{post_id}' is not found"
