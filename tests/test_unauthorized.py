class TestNotAuthorized:
    def test_not_authorized_me(self, class_client):
        response = class_client.get("/users/me")
        assert response.status_code == 401, response.text

    def test_not_authorized_posts(self, class_client, payload):
        response = class_client.get("/posts")
        assert response.status_code == 401, response.text

        response = class_client.post("/posts", json=payload)
        assert response.status_code == 401, response.text

        response = class_client.get("/posts/0")
        assert response.status_code == 401, response.text

        response = class_client.patch("/posts/0", json=payload)
        assert response.status_code == 401, response.text

        response = class_client.delete("/posts/0")
        assert response.status_code == 401, response.text

        response = class_client.post("/posts/0/comment", json="string")
        assert response.status_code == 401, response.text

        response = class_client.post("/posts/0/comment/0", json="string")
        assert response.status_code == 401, response.text

    def test_not_authorized_drafts(self, class_client, payload):
        response = class_client.get("/drafts")
        assert response.status_code == 401, response.text

        response = class_client.get("/drafts/0")
        assert response.status_code == 401, response.text

        response = class_client.put("/drafts/0", json=payload)
        assert response.status_code == 401, response.text

        response = class_client.delete("/drafts/0")
        assert response.status_code == 401, response.text

        response = class_client.post("/drafts/0/publish")
        assert response.status_code == 401, response.text
