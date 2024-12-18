"""added profile image hash

Revision ID: 62e37dc88f81
Revises: 0866fce9e7ce
Create Date: 2024-12-16 15:46:10.551138

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '62e37dc88f81'
down_revision: Union[str, None] = '0866fce9e7ce'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('profile_image_hash', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'profile_image_hash')
    # ### end Alembic commands ###
