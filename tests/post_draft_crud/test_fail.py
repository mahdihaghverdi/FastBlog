import uuid

import pytest

from tests.conftest import signup_and_auth


@pytest.mark.parametrize("endpoint", ["/posts", "drafts"])
def test_get_post(client, endpoint):
    post_id = uuid.uuid4()
    headers = signup_and_auth(client)
    response = client.get(f"{endpoint}/{post_id}", headers=headers)
    assert response.status_code == 404, response.text


@pytest.mark.parametrize("endpoint", ["/posts", "drafts"])
def test_update_post(client, endpoint):
    post_id = uuid.uuid4()
    headers = signup_and_auth(client)
    response = client.put(
        f"{endpoint}/{post_id}",
        json={"title": "a", "body": "b"},
        headers=headers,
    )
    assert response.status_code == 404, response.text


@pytest.mark.parametrize("endpoint", ["/posts", "drafts"])
def test_delete_post(client, endpoint):
    post_id = uuid.uuid4()
    headers = signup_and_auth(client)
    response = client.delete(f"{endpoint}/{post_id}", headers=headers)
    assert response.status_code == 404, response.text
