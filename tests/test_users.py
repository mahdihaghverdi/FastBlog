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
        username = data["username"]
        return username

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
        username = self.extract(data)
        assert username == self.username

        access_token = client.post(
            "/auth/access-token",
            data=self.access_token_data,
        ).json()["access_token"]

        headers = {"Authorization": f"Bearer {access_token}"}

        posts = client.get("/posts", headers=headers).json()
        assert not posts

        drafts = client.get("/drafts", headers=headers).json()
        assert not drafts

        response = client.post("/users/signup", data=self.data)
        assert response.status_code == 400, response.text

    def test_empty_users_me_posts_drafts(self, client):
        client.post("/users/signup", data=self.data)

        access_token = client.post(
            "/auth/access-token",
            data=self.access_token_data,
        ).json()["access_token"]

        headers = {"Authorization": f"Bearer {access_token}"}

        posts = client.get("/posts", headers=headers).json()
        assert not posts

        drafts = client.get("/drafts", headers=headers).json()
        assert not drafts
