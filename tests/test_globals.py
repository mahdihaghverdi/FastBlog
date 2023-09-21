def test_get_global_post(client, payload, headers):
    post = client.post("/posts", json=payload, headers=headers).json()

    response = client.get(post["url"])
    post = response.json()
    assert response.status_code == 200, response.text

    assert post["title"] == payload["title"]
    assert post["body"] == payload["body"]


def test_get_global_post_not_found(client, payload, headers):
    response = client.get("http://testserver/@mahdi2/lksjdflijsdfl")
    assert response.status_code == 404, response.text
