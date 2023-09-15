from datetime import datetime

from sqlalchemy import ForeignKey, BigInteger, Integer, Table, Column
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(AsyncAttrs, DeclarativeBase):
    id: Mapped[int] = mapped_column(
        BigInteger().with_variant(Integer, "sqlite"),
        primary_key=True,
        autoincrement=True,
    )
    created: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    async def dict(self):
        return {
            "id": await self.awaitable_attrs.id,
            "created": await self.awaitable_attrs.created,
        }


association_table = Table(
    "association_table",
    Base.metadata,
    Column("post_id", ForeignKey("posts.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)


class PostModel(Base):
    __tablename__ = "posts"

    title: Mapped[str]
    body: Mapped[str]
    url: Mapped[str]

    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    user: Mapped["UserModel"] = relationship(back_populates="posts")

    tags: Mapped[set["TagModel"]] = relationship(
        secondary=association_table,
        lazy="selectin",
    )

    def sync_dict(self):
        return {
            "id": self.id,
            "created": self.created,
            "title": self.title,
            "body": self.body,
            "url": self.url,
            "tags": sorted(tag.name for tag in self.tags),
        }


class TagModel(Base):
    __tablename__ = "tags"

    name: Mapped[str] = mapped_column(unique=True)

    async def dict(self):
        d = {"name": self.name}
        return d

    def __repr__(self):
        return f"<TagModel: id={self.id}, name={self.name!r}>"


class UserModel(Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[str]

    posts: Mapped[list["PostModel"]] = relationship(
        back_populates="user",
        cascade="delete, delete-orphan",
        lazy="selectin",
    )

    draft_posts: Mapped[list["DraftModel"]] = relationship(
        back_populates="user",
        cascade="delete, delete-orphan",
        lazy="selectin",
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
    __tablename__ = "drafts"

    title: Mapped[str]
    body: Mapped[str]

    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
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
