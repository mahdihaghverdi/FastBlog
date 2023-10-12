from sqlalchemy import update, select, func, String
from sqlalchemy.sql import expression
from sqlalchemy_utils import Ltree
from sqlalchemy_utils.types.ltree import LQUERY, LtreeType

from src.repository.models import CommentModel, PostModel
from src.repository.repos import BaseRepo, OneToManyRelRepoMixin
from src.web.core.schemas import ReplyLevel


class CommentRepo(OneToManyRelRepoMixin, BaseRepo[CommentModel]):
    def __init__(self, session):
        super().__init__(session=session, model=CommentModel)

    async def add(self, username, data) -> dict:
        record = await super().add(username, data)

        if data["parent_id"] is None:
            add_path_stmt = (
                update(self.model)
                .where(self.model.id == record.id)
                .values(path=Ltree(str(record.id)))
            )
        else:
            # new_path: parent_path + self.id
            parent_path_stmt = select(self.model.path).where(
                self.model.id == data["parent_id"],
            )
            parent_path = (await self.session.execute(parent_path_stmt)).scalar_one()
            add_path_stmt = (
                update(self.model)
                .where(self.model.id == record.id)
                .values(path=Ltree(parent_path) + Ltree(str(record.id)))
            )
        await self.session.execute(add_path_stmt)

        to_ret = record.sync_dict()
        to_ret["reply_count"] = 0
        return to_ret

    async def update(self, username, self_id, data) -> dict | None:
        comment = await super().update(username, self_id, data)
        if comment is None:
            return None
        comment = comment.sync_dict()

        reply_count = (
            await self.session.execute(
                select(func.count() - 1).filter(
                    self.model.path.descendant_of(
                        expression.cast(
                            expression.cast(
                                select(self.model.path)
                                .where(self.model.id == self_id)
                                .scalar_subquery(),
                                String,
                            ),
                            LtreeType,
                        ),
                    ),
                ),
            )
        ).scalar()
        comment["reply_count"] = reply_count
        return comment

    def _reply_count_of(self, stmt):
        return (
            (
                select(func.count() - 1).filter(
                    self.model.path.descendant_of(
                        expression.cast(
                            expression.cast(stmt.columns.path, String),
                            LtreeType,
                        ),
                    ),
                )
            )
            .scalar_subquery()
            .label("reply_count")
        )

    async def list(self, post_id, comment_id, reply_level) -> list[dict]:
        # Base query
        """
        select *,
          (
            select count(*)-1
            from comments
            where path <@ c.path::varchar::ltree
          ) as reply_count
        from comments as c
        where post_id = 30 and c.path ~ '*{1}'::lquery;    <--- level of replies ----> {1,n}

         post_id | parent_id | comment | id |          created           | user_id | path | reply_count
        ---------+-----------+---------+----+----------------------------+---------+------+-------------
              30 |           | first   | 33 | 2023-09-22 12:04:03.000081 |       1 | 33   |           4
              30 |           | first   | 34 | 2023-09-22 12:04:20.650722 |       1 | 34   |          26
        (2 rows)

        ------------------------------------------------------------------------------------------------------------------------

        select *,
          (
            select count(*)-1
            from comments
            where path <@ c.path::varchar::ltree
          ) as reply_count
        from comments as c
        where post_id = 30
              and path ~ '*{1,2}'::lquery limit 10;

         post_id | parent_id |         comment         | id |          created           | user_id | path  | reply_count
        ---------+-----------+-------------------------+----+----------------------------+---------+-------+-------------
              30 |        34 | new reply!!!!           | 62 | 2023-09-22 14:17:46.215701 |       1 | 34.62 |           0
              30 |           | first                   | 33 | 2023-09-22 12:04:03.000081 |       1 | 33    |           4
              30 |           | first                   | 34 | 2023-09-22 12:04:20.650722 |       1 | 34    |          26
              30 |        33 | Fuck comment with id 33 | 35 | 2023-09-22 12:58:00.741881 |       1 | 33.35 |           3
              30 |        34 | new reply!!!!           | 38 | 2023-09-22 12:59:56.943715 |       1 | 34.38 |           0
              30 |        34 | new reply!!!!           | 40 | 2023-09-22 14:17:36.83443  |       1 | 34.40 |           0
              30 |        34 | new reply!!!!           | 41 | 2023-09-22 14:17:40.143331 |       1 | 34.41 |           0
              30 |        34 | new reply!!!!           | 42 | 2023-09-22 14:17:41.016705 |       1 | 34.42 |           0
              30 |        34 | new reply!!!!           | 43 | 2023-09-22 14:17:41.72033  |       1 | 34.43 |           0
              30 |        34 | new reply!!!!           | 44 | 2023-09-22 14:17:42.465742 |       1 | 34.44 |           0
        (10 rows)

        """  # noqa: E501

        # Specific comment with some level
        """
         select *,
           (
             select count(*)-1
             from comments
             where path <@ c.path::varchar::ltree
           ) as reply_count
         from comments as c
         where c.path ~ '*.33.*{0,3}'::lquery;   <--- comments.id <= 33
 select *, (select count(*)-1 from comments where path <@ c.path::varchar::ltree) as reply_count from comments as c where post_id = 30 and
 path ~ '*{1}'::lquery;
 post_id | parent_id | comment | id |          created           | user_id | path | reply_count
---------+-----------+---------+----+----------------------------+---------+------+-------------
      30 |           | first   | 33 | 2023-09-22 12:04:03.000081 |       1 | 33   |           4
      30 |           | first   | 34 | 2023-09-22 12:04:20.650722 |       1 | 34   |          26
(2 rows)

 post_id | parent_id |         comment         | id |          created           | user_id |    path     | reply_count
---------+-----------+-------------------------+----+----------------------------+---------+-------------+-------------
      30 |        36 | Hello from Reza         | 65 | 2023-09-25 17:53:45.337907 |       1 | 33.35.36.65 |           0
      30 |           | first                   | 33 | 2023-09-22 12:04:03.000081 |       1 | 33          |           4
      30 |        33 | Fuck comment with id 33 | 35 | 2023-09-22 12:58:00.741881 |       1 | 33.35       |           3
      30 |        35 | Fuck comment with id 35 | 36 | 2023-09-22 12:58:31.830025 |       1 | 33.35.36    |           1
      30 |        35 | new reply               | 37 | 2023-09-22 12:59:41.37042  |       1 | 33.35.37    |           0
(5 rows)
        """  # noqa: E501

        if comment_id == 0:
            # only the base comments
            if reply_level is ReplyLevel.BASE:
                # no reps
                stmt = (
                    select(
                        self.model.id,
                        self.model.created,
                        self.model.comment,
                        self.model.parent_id,
                        expression.cast(self.model.path, String),
                        self.model.post_id,
                        self.model.username,
                    )
                    .join(PostModel, PostModel.id == post_id)
                    .filter(
                        self.model.path.lquery(
                            expression.cast(expression.cast("*{1}", String), LQUERY),
                        ),
                    )
                    .order_by("path")
                ).subquery()
            else:
                stmt = (
                    select(
                        self.model.id,
                        self.model.created,
                        self.model.comment,
                        self.model.parent_id,
                        expression.cast(self.model.path, String),
                        self.model.post_id,
                        self.model.username,
                    )
                    .join(PostModel, PostModel.id == post_id)
                    .filter(
                        self.model.path.lquery(
                            expression.cast(
                                expression.cast(
                                    "*{1," + str(int(reply_level.value) + 1) + "}",
                                    String,
                                ),
                                LQUERY,
                            ),
                        ),
                    )
                    .order_by("path")
                ).subquery()
            comments = select(stmt, self._reply_count_of(stmt))
        else:
            # other comments
            if reply_level is ReplyLevel.BASE:
                stmt = (
                    select(
                        self.model.id,
                        self.model.created,
                        self.model.comment,
                        self.model.parent_id,
                        expression.cast(self.model.path, String),
                        self.model.post_id,
                        self.model.username,
                    )
                    .filter(
                        self.model.path.lquery(
                            expression.cast(
                                expression.cast(
                                    "*."
                                    + str(comment_id)
                                    + ".*{1,"
                                    + str(int(reply_level.value) + 1)
                                    + "}",
                                    String,
                                ),
                                LQUERY,
                            ),
                        ),
                    )
                    .order_by("path")
                ).subquery()
            else:
                stmt = (
                    select(
                        self.model.id,
                        self.model.created,
                        self.model.comment,
                        self.model.parent_id,
                        expression.cast(self.model.path, String),
                        self.model.post_id,
                        self.model.username,
                    )
                    .filter(
                        self.model.path.lquery(
                            expression.cast(
                                expression.cast(
                                    "*."
                                    + str(comment_id)
                                    + ".*{1,"
                                    + str(int(reply_level.value) + 1)
                                    + "}",
                                    String,
                                ),
                                LQUERY,
                            ),
                        ),
                    )
                    .order_by("path")
                ).subquery()
            comments = select(stmt, self._reply_count_of(stmt))
        comments_mappings = (
            (await self.session.execute(comments.order_by("created"))).mappings().all()
        )
        return list(map(dict, comments_mappings))
