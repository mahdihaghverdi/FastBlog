"""change 'draft_posts' to 'drafts' all places

Revision ID: 1e42c659b916
Revises: af812abcc174
Create Date: 2023-09-13 15:15:05.550855

"""
from collections.abc import Sequence


# revision identifiers, used by Alembic.
revision: str = "1e42c659b916"
down_revision: str | None = "af812abcc174"
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
