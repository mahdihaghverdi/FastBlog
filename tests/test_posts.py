import random


class BaseTest:
    @classmethod
    def setup_class(cls):
        cls.title = "Python 3.11"
        cls.body = "Wow, such a release!"
        cls.tags = ["python", "programming"]
        cls.url = "http://testserver/@string/python-3-11"

    @property
    def payload(self):
        return {"title": self.title, "body": self.body, "tags": self.tags}

    @staticmethod
    def extract(post_data):
        title, body, _url, tags = (
            post_data["title"],
            post_data["body"],
            post_data["url"],
            post_data["tags"],
        )
        url = _url[: len(_url) - 9]
        return title, body, url, tags


class TestPostPost(BaseTest):
    @classmethod
    def setup_class(cls):
        super().setup_class()

        cls.new_slug = "the Ugly umbrella"
        cls.new_url = "http://testserver/@string/the-ugly-umbrella"

    @property
    def custom_data(self):
        d = self.payload
        d["title_in_url"] = self.new_slug
        return d

    def test_create_post_with_default_url(self, client, headers):
        response = client.post("/posts", json=self.payload, headers=headers)
        assert response.status_code == 201, response.text
        title, body, url, tags = self.extract(response.json())

        assert title == self.title
        assert body == self.body
        assert url == self.url
        assert set(tags) == set(self.tags)

    def test_create_post_with_custom_url(self, client, headers):
        response = client.post("/posts", json=self.custom_data, headers=headers)
        assert response.status_code == 201, response.text
        title, body, url, tags = self.extract(response.json())

        assert title == self.title
        assert body == self.body
        assert url == self.new_url
        assert set(tags) == set(self.tags)


class TestGetPost(BaseTest):
    def test_get_posts(self, client, headers, headers2):
        response = client.get("/posts", headers=headers)
        assert response.status_code == 200, response.text
        assert response.json() == []

        client.post("/posts", json=self.payload, headers=headers2)
        assert len(client.get("/posts", headers=headers2).json()) == 1
        assert len(client.get("/posts", headers=headers).json()) == 0

        post1 = client.post(
            "/posts",
            json={"title": "0", "body": "b1", "tags": ["1"]},
            headers=headers,
        ).json()["title"]
        post2 = client.post(
            "/posts",
            json={"title": "1", "body": "b2", "tags": ["1"]},
            headers=headers,
        ).json()["title"]
        post3 = client.post(
            "/posts",
            json={"title": "2", "body": "b3", "tags": ["1"]},
            headers=headers,
        ).json()["title"]
        post4 = client.post(
            "/posts",
            json={"title": "3", "body": "b4", "tags": ["1"]},
            headers=headers,
        ).json()["title"]
        post5 = client.post(
            "/posts",
            json={"title": "4", "body": "b5", "tags": ["1"]},
            headers=headers,
        ).json()["title"]
        post6 = client.post(
            "/posts",
            json={"title": "5", "body": "b6", "tags": ["1"]},
            headers=headers,
        ).json()["title"]
        post7 = client.post(
            "/posts",
            json={"title": "6", "body": "b7", "tags": ["1"]},
            headers=headers,
        ).json()["title"]
        post8 = client.post(
            "/posts",
            json={"title": "7", "body": "b8", "tags": ["1"]},
            headers=headers,
        ).json()["title"]
        post9 = client.post(
            "/posts",
            json={"title": "8", "body": "b9", "tags": ["1"]},
            headers=headers,
        ).json()["title"]
        post10 = client.post(
            "/posts",
            json={"title": "9", "body": "b10", "tags": ["1"]},
            headers=headers,
        ).json()["title"]

        posts = [post1, post2, post3, post4, post5, post6, post7, post8, post9, post10]

        # default query params: page = 1, per-page = 5, sort = date, desc = true
        # pages
        response = client.get("/posts", headers=headers)
        assert len(response.json()) == 5

        response = client.get("/posts", params={"page": 2}, headers=headers)
        assert len(response.json()) == 5

        response = client.get("/posts", params={"page": 3}, headers=headers)
        assert len(response.json()) == 0

        # per-page
        response = client.get("/posts", params={"per-page": 1}, headers=headers)
        assert len(response.json()) == 1

        response = client.get("/posts", params={"per-page": 2}, headers=headers)
        assert len(response.json()) == 2

        response = client.get("/posts", params={"per-page": 10}, headers=headers)
        assert len(response.json()) == 10

        response = client.get("/posts", params={"per-page": 20}, headers=headers)
        assert len(response.json()) == 10

        response = client.get(
            "/posts",
            params={"per-page": len(posts)},
            headers=headers,
        )
        assert len(response.json()) == len(posts)

        # sort
        response = client.get(
            "/posts",
            params={"per-page": len(posts)},
            headers=headers,
        )

        assert [post["title"] for post in response.json()] == posts[::-1]

        response = client.get(
            "/posts",
            params={"per-page": len(posts), "sort": "title"},
            headers=headers,
        )
        assert [post["title"] for post in response.json()] == sorted(
            posts,
            reverse=True,
        )

        # desc
        response = client.get(
            "/posts",
            params={"per-page": len(posts), "desc": "false"},
            headers=headers,
        )
        assert [post["title"] for post in response.json()] == posts

    def test_get_post(self, client, headers):
        post_id = client.post("/posts", json=self.payload, headers=headers).json()["id"]

        response = client.get(f"posts/{post_id}", headers=headers)
        title, body, url, tags = self.extract(response.json())

        assert title == self.title
        assert body == self.body
        assert url == self.url
        assert set(tags) == set(self.tags)


class TestPatchPost(TestPostPost):
    test_create_post_with_default_url = None
    test_create_post_with_custom_url = None

    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.new_tags = ["1", "2", "3"]

    @staticmethod
    def extract(post_data):
        t, b, u, ta = BaseTest.extract(post_data)
        return post_data["id"], t, b, u, ta

    def test_update_title(self, client, headers):
        post_id = client.post("/posts", json=self.payload, headers=headers).json()["id"]
        response = client.patch(
            f"/posts/{post_id}",
            json={"title": "new title"},
            headers=headers,
        )

        assert response.status_code == 200, response.text

        id_, title, body, url, tags = self.extract(response.json())

        assert id_ == post_id
        assert title == "new title"
        assert body == self.body
        assert url == self.url
        assert set(tags) == set(self.tags)

    def test_update_body(self, client, headers):
        post_id = client.post("/posts", json=self.payload, headers=headers).json()["id"]
        response = client.patch(
            f"/posts/{post_id}",
            json={"body": "new body"},
            headers=headers,
        )

        assert response.status_code == 200, response.text

        id_, title, body, url, tags = self.extract(response.json())

        assert id_ == post_id
        assert title == self.title
        assert body == "new body"
        assert url == self.url
        assert set(tags) == set(self.tags)

    def test_update_url(self, client, headers):
        post_id = client.post("/posts", json=self.payload, headers=headers).json()["id"]
        response = client.patch(
            f"/posts/{post_id}",
            json={"title_in_url": self.new_slug},
            headers=headers,
        )
        assert response.status_code == 200, response.text

        id_, title, body, url, tags = self.extract(response.json())

        assert id_ == post_id
        assert title == self.title
        assert body == self.body
        assert url == self.new_url
        assert set(tags) == set(self.tags)

    def test_update_tags(self, client, headers):
        post_id = client.post("/posts", json=self.payload, headers=headers).json()["id"]
        response = client.patch(
            f"/posts/{post_id}",
            json={"tags": self.new_tags},
            headers=headers,
        )
        assert response.status_code == 200, response.text
        id_, title, body, url, tags = self.extract(response.json())

        assert id_ == post_id
        assert title == self.title
        assert body == self.body
        assert url == self.url
        assert set(tags) == set(self.new_tags)


def test_delete_post(client, headers, payload):
    post_id = client.post("/posts", json=payload, headers=headers).json()["id"]

    response = client.delete(f"posts/{post_id}", headers=headers)
    assert response.status_code == 204, response.text
    assert client.get(f"/posts{post_id}").status_code == 404


def test_get_post_fail(client, headers):
    response = client.get(f"/posts/{random.randint(0, 1)}", headers=headers)
    assert response.status_code == 404, response.text


def test_update_post_fail(client, headers, payload):
    response = client.patch(
        f"/posts/{random.randint(0, 1)}",
        json=payload,
        headers=headers,
    )
    assert response.status_code == 404, response.text


def test_delete_post_fail(client, headers):
    response = client.delete(f"/posts/{random.randint(0, 1)}", headers=headers)
    assert response.status_code == 404, response.text
