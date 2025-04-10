"""added nullable to quadrature_from and quadrature_to

Revision ID: a98e3dce5a22
Revises: 35fb20a91c4f
Create Date: 2025-01-16 18:55:42.953577

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a98e3dce5a22'
down_revision: Union[str, None] = '35fb20a91c4f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('advertisements', 'quadrature_from',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('advertisements', 'quadrature_to',
               existing_type=sa.INTEGER(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('advertisements', 'quadrature_to',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('advertisements', 'quadrature_from',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###
