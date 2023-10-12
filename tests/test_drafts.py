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
        title, body, _url, tags, username = (
            post_data["title"],
            post_data["body"],
            post_data["url"],
            post_data["tags"],
            post_data["username"],
        )
        url = _url[: len(_url) - 9]
        return title, body, url, tags, username

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
        title, body, url, tags, username = self.publish_extract(
            client.get(f"/posts/{post_id}", headers=headers).json(),
        )
        assert title == self.title
        assert body == self.body
        assert url == self.url
        assert set(tags) == set(self.tags)
        assert username == "string"

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
        title, body, url, tags, username = self.publish_extract(
            client.get(f"/posts/{post_id}", headers=headers).json(),
        )
        assert title == self.title
        assert body == self.body
        assert url == self.new_url
        assert set(tags) == set(self.tags)
        assert username == "string"


class TestGetDraft(BaseTest):
    def test_get_drafts(self, client, headers, headers2):
        response = client.get("/drafts", headers=headers)
        assert response.status_code == 200, response.text
        assert response.json() == []

        client.post("/drafts", json=self.payload, headers=headers2)
        assert len(client.get("/drafts", headers=headers2).json()) == 1
        assert len(client.get("/drafts", headers=headers).json()) == 0

        post1 = client.post(
            "/drafts",
            json={"title": "1", "body": "b1"},
            headers=headers,
        ).json()
        post2 = client.post(
            "/drafts",
            json={"title": "2", "body": "b2"},
            headers=headers,
        ).json()
        post3 = client.post(
            "/drafts",
            json={"title": "3", "body": "b3"},
            headers=headers,
        ).json()
        post4 = client.post(
            "/drafts",
            json={"title": "4", "body": "b4"},
            headers=headers,
        ).json()
        post5 = client.post(
            "/drafts",
            json={"title": "5", "body": "b5"},
            headers=headers,
        ).json()
        post6 = client.post(
            "/drafts",
            json={"title": "6", "body": "b6"},
            headers=headers,
        ).json()
        post7 = client.post(
            "/drafts",
            json={"title": "7", "body": "b7"},
            headers=headers,
        ).json()
        post8 = client.post(
            "/drafts",
            json={"title": "8", "body": "b8"},
            headers=headers,
        ).json()
        post9 = client.post(
            "/drafts",
            json={"title": "9", "body": "b9"},
            headers=headers,
        ).json()
        post10 = client.post(
            "/drafts",
            json={"title": "10", "body": "b10"},
            headers=headers,
        ).json()

        posts = [post1, post2, post3, post4, post5, post6, post7, post8, post9, post10]

        # default query params:
        # page = 1,
        # per-page = 5,
        # sort = date,
        # desc = true

        # pages
        response = client.get("/drafts", headers=headers)
        assert len(response.json()) == 5

        response = client.get("/drafts", params={"page": 2}, headers=headers)
        assert len(response.json()) == 5

        response = client.get("/drafts", params={"page": 3}, headers=headers)
        assert len(response.json()) == 0

        # per-page
        response = client.get("/drafts", params={"per-page": 1}, headers=headers)
        assert len(response.json()) == 1

        response = client.get("/drafts", params={"per-page": 2}, headers=headers)
        assert len(response.json()) == 2

        response = client.get("/drafts", params={"per-page": 10}, headers=headers)
        assert len(response.json()) == 10

        response = client.get("/drafts", params={"per-page": 20}, headers=headers)
        assert len(response.json()) == 10

        # sort
        response = client.get(
            "/drafts",
            params={"per-page": 20},
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


class TestPutDraft:
    @staticmethod
    def extract(data):
        return data["title"], data["body"], data["updated"]

    def test_update_draft(self, client, headers, payload):
        new_title, new_body = "a", "b"
        draft_id = client.post("/drafts", json=payload, headers=headers).json()["id"]

        response = client.put(
            f"/drafts/{draft_id}",
            json={"title": new_title, "body": new_body},
            headers=headers,
        )
        assert response.status_code == 200, response.text

        title, body, updated = self.extract(response.json())
        assert title == new_title
        assert body == new_body
        assert updated is not None


def test_delete_draft(client, headers, payload):
    response = client.post("/drafts", json=payload)
    assert response.status_code == 401, response.text

    draft_id = client.post("/drafts", json=payload, headers=headers).json()["id"]

    response = client.delete(f"/drafts/{draft_id}", headers=headers)
    assert response.status_code == 204, response.text
    assert not client.get("/posts", headers=headers).json()
    assert client.get(f"/posts{draft_id}").status_code == 404
