"""make path sqlitable

Revision ID: 6e4a0b3ff89b
Revises: a04fe646af6d
Create Date: 2023-09-30 20:53:56.365184

"""
from collections.abc import Sequence


# revision identifiers, used by Alembic.
revision: str = "6e4a0b3ff89b"
down_revision: str | None = "a04fe646af6d"
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