from datetime import datetime

from sqlalchemy import ForeignKey, BigInteger, Integer, Table, Column, String
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

    def __repr__(self):
        return (
            f"<PostModel: "
            f"title={self.title!r}, "
            f"body={self.body!r}, "
            f"url={self.url!r}, "
            f"tags={self.tags!r}>"
        )

    def sync_dict(self):
        return {
            "id": self.id,
            "created": self.created,
            "title": self.title,
            "body": self.body,
            "url": self.url,
            # "tags": [{'name': tag.name for tag in self.tags}],
            "tags": sorted(
                [tag.sync_dict() for tag in self.tags],
                key=lambda x: x["name"],
            ),
        }


class TagModel(Base):
    __tablename__ = "tags"

    name: Mapped[str] = mapped_column(unique=True)

    def __repr__(self):
        return f"<TagModel: name={self.name!r}>"

    def sync_dict(self):
        return {"name": self.name}


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

    def sync_dict(self):
        return {
            "id": self.id,
            "created": self.created,
            "username": self.username,
            "password": self.password,
        }

    async def dict(self):
        d = await super().dict()
        d.update(
            {
                "username": self.username,
                "password": self.password,
                "posts": await self.awaitable_attrs.posts,
                "drafts": await self.awaitable_attrs.draft_posts,
            },
        )
        return d


class DraftModel(Base):
    __tablename__ = "drafts"

    title: Mapped[str]
    body: Mapped[str]

    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    user: Mapped["UserModel"] = relationship(back_populates="draft_posts")

    def __repr__(self):
        return f"<DraftPost: {self.title!r}>"

    def sync_dict(self):
        return {
            "id": self.id,
            "created": self.created,
            "title": self.title,
            "body": self.body,
        }


class CommentModel(Base):
    __tablename__ = "comments"
    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id"))
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("comments.id"))
    comment: Mapped[str] = mapped_column(String(255))
    children = relationship("CommentModel", cascade="delete, delete-orphan")

    def sync_dict(self):
        return {
            "id": self.id,
            "created": self.created,
            "post_id": self.post_id,
            "parent_id": self.parent_id,
            "comment": self.comment,
        }
