import random


class TestPostsNotFound:
    def test_get_post(self, class_client, class_headers):
        response = class_client.get("/posts/0", headers=class_headers)
        assert response.status_code == 404, response.text
        assert "post" in response.text.lower()

    def test_update_post(self, class_client, class_headers, payload):
        response = class_client.patch("/posts/0", json=payload, headers=class_headers)
        assert response.status_code == 404, response.text
        assert "post" in response.text.lower()

    def test_delete_post(self, class_client, class_headers):
        response = class_client.delete("/posts/0", headers=class_headers)
        assert response.status_code == 404, response.text
        assert "post" in response.text.lower()

    def test_add_comment(self, class_client, class_headers):
        response = class_client.post(
            "/posts/0/comment",
            headers=class_headers,
            json="comment",
        )
        assert response.status_code == 404, response.text
        assert "post" in response.text.lower()

    def test_add_reply(self, class_client, class_headers):
        response = class_client.post(
            "/posts/0/comment/0",
            headers=class_headers,
            json="comment",
        )
        assert response.status_code == 404, response.text
        assert "post" in response.text.lower()


class TestDraftsNotFound:
    def test_get_draft(self, class_client, class_headers):
        response = class_client.get("/drafts/0", headers=class_headers)
        assert response.status_code == 404, response.text
        assert "draft" in response.text.lower()

    def test_update_draft(self, class_client, class_headers, payload):
        response = class_client.put(
            "/drafts/0",
            json=payload,
            headers=class_headers,
        )
        assert response.status_code == 404, response.text
        assert "draft" in response.text.lower()

    def test_delete_draft(self, class_client, class_headers):
        response = class_client.delete("/drafts/0", headers=class_headers)
        assert response.status_code == 404, response.text
        assert "draft" in response.text.lower()

    def test_publish_draft(self, class_client, class_headers):
        response = class_client.post(
            f"/drafts/{random.randint(0, 2)}/publish",
            headers=class_headers,
            json={"tags": ["1"]},
        )
        assert response.status_code == 404, response.text
        assert "draft" in response.text.lower()


class TestGlobalNotFound:
    def test_user(self, client, payload, headers):
        response = client.get("http://testserver/@mahdi2/lksjdflijsdfl")
        assert response.status_code == 404, response.text
        assert "user" in response.text.lower()

    def test_post(self, client, payload, headers):
        response = client.get("http://testserver/@string/lksjdflijsdfl")
        assert response.status_code == 404, response.text
        assert "post" in response.text.lower()


class TestCommentsNotFound:
    def test_add_reply(self, client, headers, payload):
        post_id = client.post("/posts", headers=headers, json=payload).json()["id"]
        response = client.post(
            f"/posts/{post_id}/comment/1000",
            json="reply",
            headers=headers,
        )
        assert response.status_code == 404, response.text
        assert "comment" in response.text.lower()

    def test_get_base_comment(self, class_client, class_headers):
        response = class_client.get("/comments/10/basecomments")
        assert response.status_code == 404, response.text
        assert "post" in response.text.lower()

    def test_update_comment_post(self, class_client, headers, payload):
        response = class_client.put(
            "/comments/10/0",
            json="updated comment",
            headers=headers,
        )
        assert response.status_code == 404, response.text
        assert "post" in response.text.lower()

    def test_update_comment_comment(self, client, headers, payload):
        post_id = client.post("/posts", headers=headers, json=payload).json()["id"]
        response = client.put(
            f"/comments/{post_id}/10",
            json="updated comment",
            headers=headers,
        )
        assert response.status_code == 404, response.text
        assert "comment" in response.text.lower()

    def test_delete_comment_post(self, class_client, headers, payload):
        response = class_client.delete(
            "/comments/10/0",
            headers=headers,
        )
        assert response.status_code == 404, response.text
        assert "post" in response.text.lower()

    def test_delete_comment_comment(self, client, headers, payload):
        post_id = client.post("/posts", headers=headers, json=payload).json()["id"]
        response = client.delete(
            f"/comments/{post_id}/10",
            headers=headers,
        )
        assert response.status_code == 404, response.text
        assert "comment" in response.text.lower()
