import uuid
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(AsyncAttrs, DeclarativeBase):
    pass


class PostModel(Base):
    __tablename__ = "posts"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    created: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    title: Mapped[str]
    body: Mapped[str]

    def dict(self):
        return {
            "id": self.id,
            "created": self.created,
            "title": self.title,
            "body": self.body,
        }
