import pytest

from tests.conftest import BaseTest


def test_add_comment(client, headers, payload):
    post_id = client.post("/posts", headers=headers, json=payload).json()["id"]
    response = client.post(
        f"/posts/{post_id}/comment",
        headers=headers,
        json="my comment",
    )
    assert response.status_code == 201, response.text

    comment_data = response.json()
    comment, parent_id, username, path, reply_count, updated = (
        comment_data["comment"],
        comment_data["parent_id"],
        comment_data["username"],
        comment_data["path"],
        comment_data["reply_count"],
        comment_data["updated"],
    )
    assert comment == "my comment"
    assert parent_id is None
    assert username == "string"
    assert path == str(comment_data["id"])
    assert reply_count == 0
    assert updated is None


class TestGetCommentsBaseCommentsNoReply:
    @pytest.mark.parametrize("reply_level", ["0", "1", "2", "3"])
    def test_get_comments_base_comments_no_replies(
        self,
        class_client,
        class_headers,
        payload,
        post_id_comments,
        reply_level,
    ):
        post_id, comments = post_id_comments
        response = class_client.get(
            f"/comments/{post_id}/basecomments",
            headers=class_headers,
            params={"reply-level": reply_level},
        )
        assert response.status_code == 200, response.text

        got_comments = response.json()
        assert len(comments) == len(comments)

        for got, had in zip(got_comments, comments):
            assert got["comment"] == had["comment"]
            assert got["parent_id"] == had["parent_id"]
            assert got["path"] == had["path"]
            assert got["username"] == had["username"]
            assert got["reply_count"] == had["reply_count"]


class TestGetCommentsBaseCommentsWithOneLevelReply(BaseTest):
    @pytest.mark.parametrize(
        ("reply_level", "comments_count"),
        [("0", 5), ("1", 10), ("2", 10), ("3", 10)],
    )
    def test(
        self,
        class_client,
        class_headers,
        payload,
        reply_level,
        comments_count,
        post_id_comments_replies,
    ):
        post_id, base_comments, replies, comments_and_replies = post_id_comments_replies
        response = class_client.get(
            f"/comments/{post_id}/basecomments",
            headers=class_headers,
            params={"reply-level": reply_level},
        )
        assert response.status_code == 200, response.text

        got_comments = response.json()
        assert (
            len(base_comments if reply_level == "0" else comments_and_replies)
            == comments_count
        )

        for got, had in zip(
            got_comments,
            base_comments if reply_level == "0" else comments_and_replies,
        ):
            assert got["comment"] == had["comment"]
            assert got["parent_id"] == had["parent_id"]
            assert got["path"] == had["path"]
            assert got["username"] == had["username"]

        if reply_level == "0":
            assert all(comment["reply_count"] == 1 for comment in got_comments)

        assert all(
            reply["reply_count"] == 0
            for reply in got_comments
            if (reply["path"].split(".")) == 1
        )


class TestGetCommentsBaseCommentsWithTwoLevelReply(BaseTest):
    @pytest.mark.parametrize(
        ("reply_level", "comments_count"),
        [("0", 5), ("1", 10), ("2", 15), ("3", 15)],
    )
    def test(
        self,
        class_client,
        class_headers,
        payload,
        reply_level,
        comments_count,
        post_id_comments_replies_two_level,
    ):
        (
            post_id,
            base_comments,
            level_one_reply,
            all_comments,
        ) = post_id_comments_replies_two_level

        response = class_client.get(
            f"/comments/{post_id}/basecomments",
            headers=class_headers,
            params={"reply-level": reply_level},
        )
        assert response.status_code == 200, response.text

        got_comments = response.json()
        match (reply_level, comments_count):
            case ("0", 5):
                assert len(base_comments) == comments_count

                for got, had in zip(got_comments, base_comments):
                    self.assert_details(got, had)

                assert all(comment["reply_count"] == 2 for comment in got_comments)

            case ("1", 10):
                assert len(base_comments + level_one_reply) == comments_count

                comments = sorted(
                    base_comments + level_one_reply,
                    key=lambda x: x["id"],
                )
                for got, had in zip(got_comments, comments):
                    self.assert_details(got, had)

                assert all(
                    one_reply["reply_count"] == 1
                    for one_reply in got_comments
                    if (one_reply["path"].split(".")) == 2
                )

            case ("2", 15):
                assert len(all_comments) == comments_count

                for got, had in zip(got_comments, all_comments):
                    self.assert_details(got, had)

                assert all(
                    two_level["reply_count"] == 0
                    for two_level in got_comments
                    if (two_level["path"].split(".")) == 3
                )

            case ("3", 15):
                assert len(all_comments) == comments_count

                for got, had in zip(got_comments, all_comments):
                    self.assert_details(got, had)

                assert all(
                    two_level["reply_count"] == 0
                    for two_level in got_comments
                    if (two_level["path"].split(".")) == 3
                )


class TestGetCommentsBaseCommentsWithThreeLevelReply(BaseTest):
    @pytest.mark.parametrize(
        ("reply_level", "comments_count"),
        [("0", 5), ("1", 10), ("2", 15), ("3", 20)],
    )
    def test(
        self,
        class_client,
        class_headers,
        payload,
        reply_level,
        comments_count,
        post_id_comments_replies_three_level,
    ):
        (
            post_id,
            base_comments,
            level_one_reply,
            level_two_reply,
            level_three_reply,
            all_comments,
        ) = post_id_comments_replies_three_level

        response = class_client.get(
            f"/comments/{post_id}/basecomments",
            headers=class_headers,
            params={"reply-level": reply_level},
        )
        assert response.status_code == 200, response.text

        got_comments = response.json()
        match (reply_level, comments_count):
            case ("0", 5):
                assert len(base_comments) == comments_count

                for got, had in zip(got_comments, base_comments):
                    self.assert_details(got, had)

                assert all(comment["reply_count"] == 3 for comment in got_comments)

            case ("1", 10):
                all_comments = base_comments + level_one_reply
                assert len(all_comments) == comments_count

                comments = sorted(all_comments, key=lambda x: x["id"])
                for got, had in zip(got_comments, comments):
                    self.assert_details(got, had)

                assert all(
                    one_reply["reply_count"] == 2
                    for one_reply in got_comments
                    if (one_reply["path"].split(".")) == 2
                )

            case ("2", 15):
                all_comments = base_comments + level_one_reply + level_two_reply
                assert len(all_comments) == comments_count

                comments = sorted(all_comments, key=lambda x: x["id"])
                for got, had in zip(got_comments, comments):
                    self.assert_details(got, had)

                assert all(
                    two_level["reply_count"] == 1
                    for two_level in got_comments
                    if (two_level["path"].split(".")) == 3
                )

            case ("3", 20):
                assert len(all_comments) == comments_count

                for got, had in zip(got_comments, all_comments):
                    self.assert_details(got, had)

                assert all(
                    two_level["reply_count"] == 0
                    for two_level in got_comments
                    if (two_level["path"].split(".")) == 4
                )


def test_update_comment(client, headers, payload):
    post_id = client.post("/posts", headers=headers, json=payload).json()["id"]
    comment_id = client.post(
        f"/posts/{post_id}/comment",
        headers=headers,
        json="my comment",
    ).json()["id"]

    response = client.put(
        f"/comments/{post_id}/{comment_id}",
        json="updated comment",
        headers=headers,
    )
    assert response.status_code == 200, response.text

    comment_data = response.json()
    comment, parent_id, username, path, reply_count, updated = (
        comment_data["comment"],
        comment_data["parent_id"],
        comment_data["username"],
        comment_data["path"],
        comment_data["reply_count"],
        comment_data["updated"],
    )
    assert comment == "updated comment"
    assert parent_id is None
    assert username == "string"
    assert path == str(comment_data["id"])
    assert reply_count == 0
    assert updated is not None


def test_delete_comment(client, headers, payload):
    post_id = client.post("/posts", headers=headers, json=payload).json()["id"]
    comment_id = client.post(
        f"/posts/{post_id}/comment",
        headers=headers,
        json="my comment",
    ).json()["id"]

    response = client.delete(
        f"/comments/{post_id}/{comment_id}",
        headers=headers,
    )
    assert response.status_code == 204, response.text
