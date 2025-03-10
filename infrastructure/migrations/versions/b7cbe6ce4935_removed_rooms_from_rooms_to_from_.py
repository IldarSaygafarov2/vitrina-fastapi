"""removed rooms_from rooms_to from advertisements

Revision ID: b7cbe6ce4935
Revises: 222ae2e67493
Create Date: 2025-01-15 00:18:19.917186

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7cbe6ce4935'
down_revision: Union[str, None] = '222ae2e67493'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('advertisements', 'rooms_qty_from')
    op.drop_column('advertisements', 'rooms_qty_to')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('advertisements', sa.Column('rooms_qty_to', sa.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('advertisements', sa.Column('rooms_qty_from', sa.INTEGER(), autoincrement=False, nullable=False))
    # ### end Alembic commands ###
