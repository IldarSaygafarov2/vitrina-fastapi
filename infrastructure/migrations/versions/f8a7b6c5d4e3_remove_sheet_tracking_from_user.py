"""remove has_spreadsheet and group sheet urls from user

Revision ID: f8a7b6c5d4e3
Revises: d9e4f5a6b7c8
Create Date: 2026-03-30

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "f8a7b6c5d4e3"
down_revision: Union[str, None] = "d9e4f5a6b7c8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column("users", "group_buy_sheet_url")
    op.drop_column("users", "group_rent_sheet_url")
    op.drop_column("users", "has_spreadsheet")


def downgrade() -> None:
    op.add_column(
        "users",
        sa.Column("has_spreadsheet", sa.Boolean(), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("group_rent_sheet_url", sa.String(length=2048), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("group_buy_sheet_url", sa.String(length=2048), nullable=True),
    )
