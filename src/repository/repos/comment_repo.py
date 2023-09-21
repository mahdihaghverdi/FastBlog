from src.repository.models import CommentModel
from src.repository.repos import BaseRepo
from src.service.objects import Comment


class CommentRepo(BaseRepo):
    def __init__(self, session):
        model = CommentModel
        object_ = Comment
        super().__init__(session=session, model=model, object_=object_)

    async def add(self, post_id, parent_id, comment):
        record = self.model(post_id=post_id, parent_id=parent_id, comment=comment)
        self.session.add(record)
        return self.object(**record.sync_dict(), model=record)
