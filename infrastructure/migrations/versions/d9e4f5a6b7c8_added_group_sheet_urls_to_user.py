"""added group sheet urls to user

Revision ID: d9e4f5a6b7c8
Revises: c8f1a2b3d4e5
Create Date: 2026-02-14

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "d9e4f5a6b7c8"
down_revision: Union[str, None] = "c8f1a2b3d4e5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("group_rent_sheet_url", sa.String(length=2048), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("group_buy_sheet_url", sa.String(length=2048), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "group_buy_sheet_url")
    op.drop_column("users", "group_rent_sheet_url")
