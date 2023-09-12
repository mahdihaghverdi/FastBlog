from datetime import datetime
from uuid import uuid4, UUID

from sqlalchemy import ForeignKey
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(AsyncAttrs, DeclarativeBase):
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    created: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    async def dict(self):
        return {
            "id": await self.awaitable_attrs.id,
            "created": await self.awaitable_attrs.created,
        }


class PostModel(Base):
    __tablename__ = "posts"

    title: Mapped[str]
    body: Mapped[str]
    url: Mapped[str]

    # TODO: see cascading in database
    user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    user: Mapped["UserModel"] = relationship(back_populates="posts")

    async def dict(self):
        d = await super().dict()
        d.update(
            {
                "title": self.title,
                "body": self.body,
                "url": self.url,
            },
        )
        return d


class UserModel(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]

    posts: Mapped[list["PostModel"]] = relationship(
        back_populates="user",
        cascade="delete, delete-orphan",
    )

    draft_posts: Mapped[list["DraftModel"]] = relationship(
        back_populates="user",
        cascade="delete, delete-orphan",
    )

    async def dict(self):
        d = await super().dict()
        d.update(
            {
                "username": self.username,
                "password": self.password,
                "posts": await self.awaitable_attrs.posts,
                "draft_posts": await self.awaitable_attrs.draft_posts,
            },
        )
        return d


class DraftModel(Base):
    __tablename__ = "draft_posts"

    title: Mapped[str]
    body: Mapped[str]

    user_id: Mapped[UUID | None] = mapped_column(ForeignKey("users.id"))
    user: Mapped["UserModel"] = relationship(back_populates="draft_posts")

    async def dict(self):
        d = await super().dict()
        d.update(
            {
                "title": self.title,
                "body": self.body,
            },
        )
        return d
