from sqlalchemy import insert, update, select
from sqlalchemy_utils import Ltree

from src.repository.models import CommentModel
from src.repository.repos import BaseRepo
from src.service.objects import Comment


class CommentRepo(BaseRepo):
    def __init__(self, session):
        model = CommentModel
        object_ = Comment
        super().__init__(session=session, model=model, object_=object_)

    async def add(self, user_id, post_id, parent_id, comment):
        insert_stmt = (
            insert(self.model)
            .values(
                user_id=user_id,
                post_id=post_id,
                parent_id=parent_id,
                comment=comment,
            )
            .returning(self.model)
        )

        record = (await self.session.execute(insert_stmt)).scalar_one()
        if parent_id is None:
            add_path_stmt = (
                update(self.model)
                .where(self.model.id == record.id)
                .values(path=Ltree(str(record.id)))
            )
        else:
            # new_path: parent_path + self.id
            parent_path_stmt = select(self.model.path).where(self.model.id == parent_id)
            parent_path = (await self.session.execute(parent_path_stmt)).scalar_one()
            add_path_stmt = (
                update(self.model)
                .where(self.model.id == record.id)
                .values(path=Ltree(parent_path) + Ltree(str(record.id)))
            )
        await self.session.execute(add_path_stmt)
        return self.object(**record.sync_dict(), model=record)
