"""added has_spreadsheet to user

Revision ID: c8f1a2b3d4e5
Revises: ea4efba8118e
Create Date: 2026-02-13

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "c8f1a2b3d4e5"
down_revision: Union[str, None] = "ea4efba8118e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("has_spreadsheet", sa.Boolean(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "has_spreadsheet")
