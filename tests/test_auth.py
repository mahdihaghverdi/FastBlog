from slugify import Slugify


class TestAuth:
    username = "string"
    password = "12345678"

    @property
    def data(self):
        return {"username": TestAuth.username, "password": TestAuth.password}

    @property
    def access_token_data(self):
        d = self.data
        d["grant_type"] = "password"
        return d

    @staticmethod
    def extract(data):
        username, posts, drafts = data["username"], data["posts"], data["drafts"]
        return username, posts, drafts

    @staticmethod
    def extract_post(data):
        title, body, url, tags = data["title"], data["body"], data["url"], data["tags"]
        return title, body, url, tags

    @staticmethod
    def extract_draft(data):
        title, body = data["title"], data["body"]
        return title, body

    def test_signup(self, client):
        response = client.post("/users/signup", data=self.data)
        assert response.status_code == 201, response.text

        data = response.json()
        username, posts, drafts = self.extract(data)
        assert username == self.username
        assert not posts
        assert not drafts

        response = client.post("/users/signup", data=self.data)
        assert response.status_code == 400, response.text

    def test_access_token(self, client):
        response = client.post("/auth/access-token", data=self.access_token_data)
        assert response.status_code == 401, response.text

        client.post("/users/signup", data=self.data)
        response = client.post("/auth/access-token", data=self.access_token_data)
        assert response.status_code == 200, response.text

        data = response.json()
        access_token, token_type = data["access_token"], data["token_type"]
        assert access_token
        assert token_type.lower() == "bearer"

        response = client.post(
            "/auth/access-token",
            data={
                "username": "hello",
                "grant_type": "password",
                "password": "12345678",
            },
        )
        assert response.status_code == 401, response.text

    def test_empty_users_me(self, client):
        client.post("/users/signup", data=self.data)
        access_token = client.post(
            "/auth/access-token",
            data=self.access_token_data,
        ).json()["access_token"]
        response = client.get(
            "/users/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        assert response.status_code == 200, response.text

        data = response.json()
        username, posts, drafts = self.extract(data)
        assert username == self.username
        assert not posts
        assert not drafts

    def test_users_me_posts_drafts(self, client, payload):
        client.post("/users/signup", data=self.data)
        access_token = client.post(
            "/auth/access-token",
            data=self.access_token_data,
        ).json()["access_token"]

        headers = {"Authorization": f"Bearer {access_token}"}
        client.post("/drafts", json=payload, headers=headers)
        client.post("/posts", json=payload, headers=headers)

        response = client.get("/users/me", headers=headers)

        username, posts, drafts = self.extract(response.json())
        assert username == self.username

        title, body, url, tags = self.extract_post(posts[0])
        assert title == payload["title"]
        assert body == payload["body"]
        s = Slugify(to_lower=True)
        assert f"http://testserver/@{self.username}/{s(title)}" == url[: len(url) - 9]
        assert tags == payload["tags"]

        title, body = self.extract_draft(drafts[0])
        assert title == payload["title"]
        assert body == payload["body"]
