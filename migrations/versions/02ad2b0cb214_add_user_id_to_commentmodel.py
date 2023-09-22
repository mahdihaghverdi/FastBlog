"""add user_id to CommentModel

Revision ID: 02ad2b0cb214
Revises: 9bd8d5519b08
Create Date: 2023-09-22 11:32:04.890360

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "02ad2b0cb214"
down_revision: str | None = "9bd8d5519b08"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "comments",
        sa.Column(
            "user_id",
            sa.BigInteger().with_variant(sa.Integer(), "sqlite"),
            nullable=False,
        ),
    )
    op.create_foreign_key(None, "comments", "users", ["user_id"], ["id"])
    op.alter_column(
        "drafts",
        "user_id",
        existing_type=sa.BIGINT(),
        nullable=False,
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "drafts",
        "user_id",
        existing_type=sa.BIGINT(),
        nullable=True,
    )
    op.drop_constraint(None, "comments", type_="foreignkey")
    op.drop_column("comments", "user_id")
    # ### end Alembic commands ###
