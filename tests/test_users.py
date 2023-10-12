class TestUsers:
    name = "mahdi"
    username = "string"
    password = "12345678"
    bio = "Hi my name is fuck"
    twitter = "somerandomid"
    email = "mahdi@mahdi.com"

    @property
    def data(self):
        return {
            "name": self.name,
            "username": self.username,
            "password": self.password,
            "bio": self.bio,
            "twitter": self.twitter,
            "email": self.email,
        }

    @staticmethod
    def extract(data):
        name = data["name"]
        username = data["username"]
        bio = data["bio"]
        twitter = data["twitter"]
        email = data["email"]
        created = data["created"]
        updated = data["updated"]
        posts = data["posts"]
        drafts = data["drafts"]
        return name, username, bio, twitter, email, created, updated, posts, drafts

    @staticmethod
    def extract_post(data):
        title, url, created = data["title"], data["url"], data["created"]
        return title, url, created

    @staticmethod
    def extract_draft(data):
        title, created = data["title"], data["created"]
        return title, created

    @property
    def access_token_data(self):
        d = {
            "username": self.username,
            "password": self.password,
            "grant_type": "password",
        }
        return d

    def test_signup_fail(self, client):
        client.post("/users/signup", json=self.data)
        response = client.post("/users/signup", json=self.data)
        assert response.status_code == 400, response.text
        assert "exists" in response.text.lower()

    def test_signup_successful(self, client):
        response = client.post("/users/signup", json=self.data)
        assert response.status_code == 201, response.text

        data = response.json()
        (
            name,
            username,
            bio,
            twitter,
            email,
            created,
            updated,
            posts,
            drafts,
        ) = self.extract(data)

        assert name == self.name
        assert username == self.username
        assert bio == self.bio
        assert twitter == self.twitter
        assert email == self.email
        assert created is not None
        assert updated is None
        assert not posts
        assert not drafts

    def test_users_me_empty(self, client):
        client.post("/users/signup", json=self.data)
        access_token = client.post(
            "/auth/access-token",
            data=self.access_token_data,
        ).json()["access_token"]

        headers = {"Authorization": f"Bearer {access_token}"}

        response = client.get("/users/me", headers=headers)
        assert response.status_code == 200, response.text

        (
            name,
            username,
            bio,
            twitter,
            email,
            created,
            updated,
            posts,
            drafts,
        ) = self.extract(response.json())
        assert name == self.name
        assert username == self.username
        assert bio == self.bio
        assert twitter == self.twitter
        assert email == self.email
        assert created is not None
        assert updated is None
        assert not posts
        assert not drafts

    def test_users_me_posts_empty_drafts(self, client, payload):
        client.post("/users/signup", json=self.data)
        access_token = client.post(
            "/auth/access-token",
            data=self.access_token_data,
        ).json()["access_token"]

        headers = {"Authorization": f"Bearer {access_token}"}

        client.post("/posts", headers=headers, json=payload)

        response = client.get("/users/me", headers=headers)
        assert response.status_code == 200, response.text

        (
            name,
            username,
            bio,
            twitter,
            email,
            created,
            updated,
            posts,
            drafts,
        ) = self.extract(response.json())
        assert name == self.name
        assert username == self.username
        assert bio == self.bio
        assert twitter == self.twitter
        assert email == self.email
        assert created is not None
        assert updated is None
        assert posts
        assert not drafts

        title, url, created = self.extract_post(posts[0])
        assert title == payload["title"]
        assert url[: len(url) - 9] == "http://testserver/@string/python-3-11"
        assert created is not None

    def test_users_me_drafts_empty_posts(self, client, payload):
        client.post("/users/signup", json=self.data)
        access_token = client.post(
            "/auth/access-token",
            data=self.access_token_data,
        ).json()["access_token"]

        headers = {"Authorization": f"Bearer {access_token}"}

        client.post("/drafts", headers=headers, json=payload)

        response = client.get("/users/me", headers=headers)
        assert response.status_code == 200, response.text

        (
            name,
            username,
            bio,
            twitter,
            email,
            created,
            updated,
            posts,
            drafts,
        ) = self.extract(response.json())
        assert name == self.name
        assert username == self.username
        assert bio == self.bio
        assert twitter == self.twitter
        assert email == self.email
        assert created is not None
        assert updated is None
        assert not posts
        assert drafts

        title, created = self.extract_draft(drafts[0])
        assert title == payload["title"]
        assert created is not None

    def test_users_me_posts_drafts(self, client, payload):
        client.post("/users/signup", json=self.data)
        access_token = client.post(
            "/auth/access-token",
            data=self.access_token_data,
        ).json()["access_token"]

        headers = {"Authorization": f"Bearer {access_token}"}

        client.post("/posts", headers=headers, json=payload)
        client.post("/drafts", headers=headers, json=payload)

        response = client.get("/users/me", headers=headers)
        assert response.status_code == 200, response.text

        (
            name,
            username,
            bio,
            twitter,
            email,
            created,
            updated,
            posts,
            drafts,
        ) = self.extract(response.json())
        assert name == self.name
        assert username == self.username
        assert bio == self.bio
        assert twitter == self.twitter
        assert email == self.email
        assert created is not None
        assert updated is None
        assert posts
        assert drafts

        title, url, created = self.extract_post(posts[0])
        assert title == payload["title"]
        assert url[: len(url) - 9] == "http://testserver/@string/python-3-11"
        assert created is not None

        title, created = self.extract_draft(drafts[0])
        assert title == payload["title"]
        assert created is not None
