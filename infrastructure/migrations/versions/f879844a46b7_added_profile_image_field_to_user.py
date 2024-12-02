"""added profile image field to user

Revision ID: f879844a46b7
Revises: 9d1f85fde39b
Create Date: 2024-12-01 20:16:37.872048

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f879844a46b7'
down_revision: Union[str, None] = '9d1f85fde39b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('profile_image', sa.String(), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'profile_image')
    # ### end Alembic commands ###