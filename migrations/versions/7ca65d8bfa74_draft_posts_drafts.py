"""draft_posts -> drafts

Revision ID: 7ca65d8bfa74
Revises: a90cc0025977
Create Date: 2023-10-10 23:04:15.023829

"""
from collections.abc import Sequence


# revision identifiers, used by Alembic.
revision: str = "7ca65d8bfa74"
down_revision: str | None = "a90cc0025977"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    pass
    # ### end Alembic commands ###