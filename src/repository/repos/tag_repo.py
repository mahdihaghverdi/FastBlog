from sqlalchemy import select

from src.repository.models import TagModel
from src.repository.repos import BaseRepo


class TagRepo(BaseRepo[TagModel]):
    def __init__(self, session):
        super().__init__(session, model=TagModel)

    async def get_or_create(self, names) -> list[TagModel]:
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
