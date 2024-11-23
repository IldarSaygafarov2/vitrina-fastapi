"""added models

Revision ID: fed01f46d11b
Revises: 9dbe6183c307
Create Date: 2024-11-23 22:22:12.849949

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fed01f46d11b'
down_revision: Union[str, None] = '9dbe6183c307'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('categories',
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('name_uz', sa.String(), nullable=False),
    sa.Column('slug', sa.String(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_categories_name'), 'categories', ['name'], unique=False)
    op.create_index(op.f('ix_categories_slug'), 'categories', ['slug'], unique=True)
    op.create_table('districts',
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('name_uz', sa.String(), nullable=False),
    sa.Column('slug', sa.String(), nullable=False),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_districts_name'), 'districts', ['name'], unique=False)
    op.create_index(op.f('ix_districts_slug'), 'districts', ['slug'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_districts_slug'), table_name='districts')
    op.drop_index(op.f('ix_districts_name'), table_name='districts')
    op.drop_table('districts')
    op.drop_index(op.f('ix_categories_slug'), table_name='categories')
    op.drop_index(op.f('ix_categories_name'), table_name='categories')
    op.drop_table('categories')
    # ### end Alembic commands ###
