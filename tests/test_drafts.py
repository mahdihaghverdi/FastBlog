import random

from tests.conftest import random_string


class BaseTest:
    @classmethod
    def setup_class(cls):
        cls.title = "Python 3.11"
        cls.body = "Wow, such a release!"
        cls.tags = ["python", "programming"]
        cls.url = "http://testserver/@string/python-3-11"

    @property
    def payload(self):
        return {"title": self.title, "body": self.body}

    @staticmethod
    def extract(post_data):
        return post_data["title"], post_data["body"]


class TestPostDraft(BaseTest):
    @classmethod
    def setup_class(cls):
        super().setup_class()
        cls.title_in_url = "an ugly umbrella"
        cls.new_url = "http://testserver/@string/an-ugly-umbrella"

    @property
    def basic_publish_payload(self):
        return {"tags": self.tags}

    @property
    def custom_publish_payload(self):
        return {"tags": self.tags, "title_in_url": self.title_in_url}

    @staticmethod
    def publish_extract(post_data):
        title, body, _url, tags = (
            post_data["title"],
            post_data["body"],
            post_data["url"],
            post_data["tags"],
        )
        url = _url[: len(_url) - 9]
        return title, body, url, tags

    def test_create_draft(self, client, headers):
        response = client.post("/drafts", json=self.payload, headers=headers)
        assert response.status_code == 201, response.text
        title, body = self.extract(response.json())
        assert title == self.title
        assert body == self.body

        response = client.get("/drafts", headers=headers)
        title, body = self.extract(response.json()[0])
        assert title == self.title
        assert body == self.body

    def test_publish_draft(self, client, headers):
        draft_id = client.post("/drafts", json=self.payload, headers=headers).json()[
            "id"
        ]
        response = client.post(
            f"/drafts/{draft_id}/publish",
            json=self.basic_publish_payload,
            headers=headers,
        )
        assert response.status_code == 200, response.text

        drafts = client.get("/drafts", headers=headers).json()
        assert not drafts

        post_id = response.json()["id"]
        title, body, url, tags = self.publish_extract(
            client.get(f"/posts/{post_id}", headers=headers).json(),
        )
        assert title == self.title
        assert body == self.body
        assert url == self.url
        assert set(tags) == set(self.tags)

    def test_publish_draft_custom_slug(self, client, headers):
        draft_id = client.post("/drafts", json=self.payload, headers=headers).json()[
            "id"
        ]
        response = client.post(
            f"/drafts/{draft_id}/publish",
            json=self.custom_publish_payload,
            headers=headers,
        )
        assert response.status_code == 200, response.text

        drafts = client.get("/drafts", headers=headers).json()
        assert not drafts

        post_id = response.json()["id"]
        title, body, url, tags = self.publish_extract(
            client.get(f"/posts/{post_id}", headers=headers).json(),
        )
        assert title == self.title
        assert body == self.body
        assert url == self.new_url
        assert set(tags) == set(self.tags)


class TestGetDraft(BaseTest):
    def test_get_drafts(self, client, headers, headers2):
        response = client.get("/drafts", headers=headers)
        assert response.status_code == 200, response.text
        assert response.json() == []

        client.post("/drafts", json=self.payload, headers=headers2)
        assert len(client.get("/drafts", headers=headers2).json()) == 1
        assert len(client.get("/drafts", headers=headers).json()) == 0

        test_drafts = [
            [{"title": random_string(), "body": random_string()} for _ in range(5)]
            for _ in range(5)
        ]

        posts = [
            client.post("/drafts", json=post, headers=headers).json()
            for post_list in test_drafts
            for post in post_list
        ]

        # default query params: page = 1, per-page = 5, sort = date, desc = true
        # pages
        response = client.get("/drafts", headers=headers)
        assert len(response.json()) == 5

        response = client.get("/drafts", params={"page": 2}, headers=headers)
        assert len(response.json()) == 5

        response = client.get("/drafts", params={"page": 3}, headers=headers)
        assert len(response.json()) == 5

        response = client.get("/drafts", params={"page": 4}, headers=headers)
        assert len(response.json()) == 5

        response = client.get("/drafts", params={"page": 5}, headers=headers)
        assert len(response.json()) == 5

        # per-page
        response = client.get("/drafts", params={"per-page": 10}, headers=headers)
        assert len(response.json()) == 10

        response = client.get("/drafts", params={"per-page": 20}, headers=headers)
        assert len(response.json()) == 20

        response = client.get(
            "/drafts",
            params={"per-page": len(posts)},
            headers=headers,
        )
        assert len(response.json()) == len(posts)

        # sort
        response = client.get(
            "/drafts",
            params={"per-page": len(posts)},
            headers=headers,
        )
        assert response.json() == posts[::-1]

        response = client.get(
            "/drafts",
            params={"per-page": len(posts), "sort": "title"},
            headers=headers,
        )
        assert response.json() == sorted(posts, key=lambda x: x["title"], reverse=True)

        # desc
        response = client.get(
            "/drafts",
            params={"per-page": len(posts), "desc": "false"},
            headers=headers,
        )
        assert response.json() == posts

    def test_get_draft(self, client, headers):
        response = client.post("/drafts", json=self.payload)
        assert response.status_code == 401, response.text

        draft_id = client.post("/drafts", json=self.payload, headers=headers).json()[
            "id"
        ]

        response = client.get(f"/drafts/{draft_id}", headers=headers)
        assert response.status_code == 200, response.text

        title, body = self.extract(response.json())
        assert title == self.title
        assert body == self.body


def test_update_draft(client, headers, payload):
    new_title, new_body = "a", "b"
    response = client.post("/drafts", json=payload)
    assert response.status_code == 401, response.text

    draft_id = client.post("/drafts", json=payload, headers=headers).json()["id"]

    response = client.put(
        f"/drafts/{draft_id}",
        json={"title": new_title, "body": new_body},
        headers=headers,
    )
    assert response.status_code == 200, response.text

    title, body = BaseTest.extract(response.json())
    assert title == new_title
    assert body == new_body


def test_delete_draft(client, headers, payload):
    response = client.post("/drafts", json=payload)
    assert response.status_code == 401, response.text

    draft_id = client.post("/drafts", json=payload, headers=headers).json()["id"]

    response = client.delete(f"/drafts/{draft_id}", headers=headers)
    assert response.status_code == 204, response.text
    assert not client.get("/posts", headers=headers).json()
    assert client.get(f"/posts{draft_id}").status_code == 404


def test_get_draft_not_found(client, headers):
    response = client.get(f"/drafts/{random.randint(0, 1)}", headers=headers)
    assert response.status_code == 404, response.text


def test_update_draft_not_found(client, headers, payload):
    response = client.put(
        f"/drafts/{random.randint(0, 1)}",
        json=payload,
        headers=headers,
    )
    assert response.status_code == 404, response.text


def test_delete_draft_not_found(client, headers):
    response = client.delete(f"/drafts/{random.randint(0, 1)}", headers=headers)
    assert response.status_code == 404, response.text


def test_publish_draft_not_found(client, headers):
    response = client.post(
        f"/drafts/{random.randint(0, 2)}/publish",
        headers=headers,
        json={"tags": ["1"]},
    )
    assert response.status_code == 404, response.text
