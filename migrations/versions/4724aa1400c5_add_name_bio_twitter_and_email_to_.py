"""add name, bio, twitter and email to UserModel

Revision ID: 4724aa1400c5
Revises: aa0f5ca3f1d4
Create Date: 2023-10-12 13:45:50.520408

"""
from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4724aa1400c5"
down_revision: str | None = "aa0f5ca3f1d4"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("users", sa.Column("name", sa.String(length=100), nullable=True))
    op.add_column("users", sa.Column("bio", sa.String(length=255), nullable=True))
    op.add_column("users", sa.Column("twitter", sa.String(), nullable=True))
    op.add_column("users", sa.Column("email", sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("users", "email")
    op.drop_column("users", "twitter")
    op.drop_column("users", "bio")
    op.drop_column("users", "name")
    # ### end Alembic commands ###
