import pytest

from tests.conftest import BaseTest


def test_add_reply(client, headers, payload):
    post_id = client.post("/posts", headers=headers, json=payload).json()["id"]
    comment_id = client.post(
        f"/posts/{post_id}/comment",
        headers=headers,
        json="my comment",
    ).json()["id"]

    response = client.post(
        f"/posts/{post_id}/comment/{comment_id}",
        headers=headers,
        json="my reply",
    )
    assert response.status_code == 201, response.text

    reply_data = response.json()
    comment, parent_id, username, path, reply_count = (
        reply_data["comment"],
        reply_data["parent_id"],
        reply_data["username"],
        reply_data["path"],
        reply_data["reply_count"],
    )
    assert comment == "my reply"
    assert parent_id == comment_id
    assert username == "string"
    assert path == f'{comment_id}.{reply_data["id"]}'
    assert reply_count == 0


class TestGetCommentsBaseRepliesOfAReply:
    @pytest.mark.parametrize("reply_level", ["0", "1", "2", "3"])
    def test(
        self,
        class_client,
        class_headers,
        payload,
        reply_level,
        post_id_comment_id_replies,
    ):
        post_id, comment_id, replies = post_id_comment_id_replies
        response = class_client.get(
            f"/comments/{post_id}/{comment_id}",
            headers=class_headers,
            params={"reply-level": reply_level},
        )
        assert response.status_code == 200, response.text

        got_replies = response.json()
        assert len(got_replies) == len(replies)
        for got, had in zip(got_replies, replies):
            assert got["comment"] == had["comment"]
            assert got["parent_id"] == had["parent_id"]
            assert got["path"] == had["path"]
            assert got["username"] == had["username"]
            assert got["reply_count"] == had["reply_count"]


class TestGetCommentsBaseRepliesWithOneLevelReply(BaseTest):
    @pytest.mark.parametrize(
        ("reply_level", "reply_count"),
        [("0", 5), ("1", 10), ("2", 10), ("3", 10)],
    )
    def test(
        self,
        class_client,
        class_headers,
        payload,
        reply_level,
        reply_count,
        post_id_comment_id_replies_one_level,
    ):
        (
            post_id,
            comment_id,
            base_replies,
            all_replies,
        ) = post_id_comment_id_replies_one_level
        response = class_client.get(
            f"/comments/{post_id}/{comment_id}",
            headers=class_headers,
            params={"reply-level": reply_level},
        )
        assert response.status_code == 200, response.text

        got_replies = response.json()
        assert len(base_replies if reply_level == "0" else all_replies) == reply_count

        for got, had in zip(
            got_replies,
            base_replies if reply_level == "0" else all_replies,
        ):
            assert got["comment"] == had["comment"]
            assert got["parent_id"] == had["parent_id"]
            assert got["path"] == had["path"]
            assert got["username"] == had["username"]

        if reply_level == "0":
            assert all(reply["reply_count"] == 1 for reply in got_replies)

        assert all(
            reply["reply_count"] == 0
            for reply in got_replies
            if (reply["path"].split(".")) == 1
        )


class TestGetCommentsBaseCommentsWithTwoLevelReply(BaseTest):
    @pytest.mark.parametrize(
        ("reply_level", "reply_count"),
        [("0", 5), ("1", 10), ("2", 15), ("3", 15)],
    )
    def test(
        self,
        class_client,
        class_headers,
        payload,
        reply_level,
        reply_count,
        post_id_comment_id_replies_two_level,
    ):
        (
            post_id,
            comment_id,
            base_replies,
            level_one_reply,
            all_replies,
        ) = post_id_comment_id_replies_two_level

        response = class_client.get(
            f"/comments/{post_id}/{comment_id}",
            headers=class_headers,
            params={"reply-level": reply_level},
        )
        assert response.status_code == 200, response.text

        got_replies = response.json()
        match (reply_level, reply_count):
            case ("0", 5):
                assert len(base_replies) == reply_count

                for got, had in zip(got_replies, base_replies):
                    self.assert_details(got, had)

                assert all(reply["reply_count"] == 2 for reply in got_replies)

            case ("1", 10):
                assert len(base_replies + level_one_reply) == reply_count

                replies = sorted(
                    base_replies + level_one_reply,
                    key=lambda x: x["id"],
                )
                for got, had in zip(got_replies, replies):
                    self.assert_details(got, had)

                assert all(
                    one_reply["reply_count"] == 1
                    for one_reply in got_replies
                    if (one_reply["path"].split(".")) == 2
                )

            case ("2", 15):
                assert len(all_replies) == reply_count

                for got, had in zip(got_replies, all_replies):
                    self.assert_details(got, had)

                assert all(
                    two_level["reply_count"] == 0
                    for two_level in got_replies
                    if (two_level["path"].split(".")) == 3
                )

            case ("3", 15):
                assert len(all_replies) == reply_count

                for got, had in zip(got_replies, all_replies):
                    self.assert_details(got, had)

                assert all(
                    two_level["reply_count"] == 0
                    for two_level in got_replies
                    if (two_level["path"].split(".")) == 3
                )


class TestGetCommentsBaseCommentsWithThreeLevelReply(BaseTest):
    @pytest.mark.parametrize(
        ("reply_level", "reply_count"),
        [("0", 5), ("1", 10), ("2", 15), ("3", 20)],
    )
    def test(
        self,
        class_client,
        class_headers,
        payload,
        reply_level,
        reply_count,
        post_id_comment_id_replies_three_level,
    ):
        (
            post_id,
            comment_id,
            base_replies,
            level_one_reply,
            level_two_reply,
            all_replies,
        ) = post_id_comment_id_replies_three_level

        response = class_client.get(
            f"/comments/{post_id}/{comment_id}",
            headers=class_headers,
            params={"reply-level": reply_level},
        )
        assert response.status_code == 200, response.text

        got_replies = sorted(response.json(), key=lambda x: x["id"])
        match (reply_level, reply_count):
            case ("0", 5):
                assert len(base_replies) == reply_count

                for got, had in zip(got_replies, base_replies):
                    self.assert_details(got, had)

                assert all(reply["reply_count"] == 3 for reply in got_replies)

            case ("1", 10):
                assert len(base_replies + level_one_reply) == reply_count

                replies = sorted(
                    base_replies + level_one_reply,
                    key=lambda x: x["id"],
                )
                for got, had in zip(got_replies, replies):
                    self.assert_details(got, had)

                assert all(
                    one_reply["reply_count"] == 1
                    for one_reply in got_replies
                    if (one_reply["path"].split(".")) == 2
                )

            case ("2", 15):
                all_replies = sorted(
                    base_replies + level_one_reply + level_two_reply,
                    key=lambda x: x["id"],
                )
                assert len(all_replies) == reply_count

                for got, had in zip(got_replies, all_replies):
                    self.assert_details(got, had)

                assert all(
                    two_level["reply_count"] == 0
                    for two_level in got_replies
                    if (two_level["path"].split(".")) == 3
                )

            case ("3", 20):
                assert len(all_replies) == reply_count

                for got, had in zip(got_replies, all_replies):
                    self.assert_details(got, had)

                assert all(
                    two_level["reply_count"] == 0
                    for two_level in got_replies
                    if (two_level["path"].split(".")) == 4
                )
