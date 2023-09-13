"""change 'draft_posts' to 'drafts'

Revision ID: af812abcc174
Revises: b216f1e9cb11
Create Date: 2023-09-13 14:49:44.600446

"""
from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "af812abcc174"
down_revision: str | None = "b216f1e9cb11"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.rename_table("draft_posts", "drafts")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.rename_table("drafts", "draft_posts")
    # ### end Alembic commands ###
