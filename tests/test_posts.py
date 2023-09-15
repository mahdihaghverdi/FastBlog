import random

from tests.conftest import test_posts


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

        posts = [
            client.post("/posts", json=post, headers=headers).json()
            for post_list in test_posts
            for post in post_list
        ]

        # default query params: page = 1, per-page = 5, sort = date, desc = true
        # pages
        response = client.get("/posts", headers=headers)
        assert len(response.json()) == 5

        response = client.get("/posts", params={"page": 2}, headers=headers)
        assert len(response.json()) == 5

        response = client.get("/posts", params={"page": 3}, headers=headers)
        assert len(response.json()) == 5

        response = client.get("/posts", params={"page": 4}, headers=headers)
        assert len(response.json()) == 5

        response = client.get("/posts", params={"page": 5}, headers=headers)
        assert len(response.json()) == 5

        # per-page
        response = client.get("/posts", params={"per-page": 10}, headers=headers)
        assert len(response.json()) == 10

        response = client.get("/posts", params={"per-page": 20}, headers=headers)
        assert len(response.json()) == 20

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
        assert response.json() == posts[::-1]

        response = client.get(
            "/posts",
            params={"per-page": len(posts), "sort": "title"},
            headers=headers,
        )
        assert response.json() == sorted(posts, key=lambda x: x["title"], reverse=True)

        # desc
        response = client.get(
            "/posts",
            params={"per-page": len(posts), "desc": "false"},
            headers=headers,
        )
        assert response.json() == posts

    def test_get_post(self, client, headers):
        post_id = client.post("/posts", json=self.payload, headers=headers).json()["id"]

        response = client.get(f"posts/{post_id}", headers=headers)
        title, body, url, tags = self.extract(response.json())

        assert title == self.title
        assert body == self.body
        assert url == self.url
        assert set(tags) == set(self.tags)


class TestPutPost(TestPostPost):
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
        payload = self.payload
        payload["title"] = "a"
        response = client.put(f"/posts/{post_id}", json=payload, headers=headers)
        assert response.status_code == 200, response.text
        id_, title, body, url, tags = self.extract(response.json())

        assert id_ == post_id
        assert title == payload["title"]
        assert body == self.body
        assert url == "http://testserver/@string/a"
        assert set(tags) == set(self.tags)

    def test_update_body(self, client, headers):
        post_id = client.post("/posts", json=self.payload, headers=headers).json()["id"]
        payload = self.payload
        payload["body"] = "a"
        response = client.put(f"/posts/{post_id}", json=payload, headers=headers)
        assert response.status_code == 200, response.text
        id_, title, body, url, tags = self.extract(response.json())

        assert id_ == post_id
        assert title == self.title
        assert body == payload["body"]
        assert url == self.url
        assert set(tags) == set(self.tags)

    def test_update_url(self, client, headers):
        post_id = client.post("/posts", json=self.payload, headers=headers).json()["id"]
        response = client.put(
            f"/posts/{post_id}",
            json=self.custom_data,
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
        payload = self.payload
        payload["tags"] = self.new_tags
        response = client.put(f"/posts/{post_id}", json=payload, headers=headers)
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
    response = client.put(
        f"/posts/{random.randint(0, 1)}",
        json=payload,
        headers=headers,
    )
    assert response.status_code == 404, response.text


def test_delete_post_fail(client, headers):
    response = client.delete(f"/posts/{random.randint(0, 1)}", headers=headers)
    assert response.status_code == 404, response.text
