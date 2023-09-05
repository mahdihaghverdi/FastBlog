def test_create_a_post(client):
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
