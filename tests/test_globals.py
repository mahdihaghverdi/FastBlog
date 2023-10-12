def test_get_global_post(client, payload, headers):
    post = client.post("/posts", json=payload, headers=headers).json()

    # add comments on the post
    # |- 1
    # |- 2
    #    |- 2.1
    #    |- 2.2
    #       |- 2.2.1
    #       |- 2.2.2
    #       |- 2.2.3
    # |- 3
    # all comments -> 8
    # base comments -> 3
    # reply_comments -> 5

    client.post(f'/posts/{post["id"]}/comment', headers=headers, json="1")
    two_id = client.post(
        f'/posts/{post["id"]}/comment',
        headers=headers,
        json="2",
    ).json()["id"]
    client.post(f'/posts/{post["id"]}/comment/{two_id}', headers=headers, json="2.1")
    two_two_id = client.post(
        f'/posts/{post["id"]}/comment/{two_id}',
        headers=headers,
        json="2.2",
    ).json()["id"]
    client.post(
        f'/posts/{post["id"]}/comment/{two_two_id}',
        headers=headers,
        json="2.2.1",
    )
    client.post(
        f'/posts/{post["id"]}/comment/{two_two_id}',
        headers=headers,
        json="2.2.2",
    )
    client.post(
        f'/posts/{post["id"]}/comment/{two_two_id}',
        headers=headers,
        json="2.2.3",
    )
    client.post(f'/posts/{post["id"]}/comment', headers=headers, json="3")

    response = client.get(post["url"])
    post = response.json()
    assert response.status_code == 200, response.text

    assert post["title"] == payload["title"]
    assert post["body"] == payload["body"]
    assert post["tags"] == payload["tags"]
    assert post["all_comments_count"] == 8
    assert post["base_comments_count"] == 3
    assert post["reply_comments_count"] == 5
