from fastapi.openapi.models import Tag
from sqlalchemy import select

from src.repository.models import TagModel
from src.repository.repos import BaseRepo


class TagRepo(BaseRepo):
    def __init__(self, session):
        model = TagModel
        object_ = Tag
        super().__init__(session, model, object_)

    async def get_or_create(self, names):
        tags = []
        for name in names:
            tag = (
                await self.session.execute(
                    select(self.model).where(self.model.name == name),
                )
            ).scalar_one_or_none()
            if tag is not None:
                tags.append(tag)
            else:
                t = self.model(name=name)
                self.session.add(t)
                tags.append(t)
        self.session.add_all(tags)
        return tags
