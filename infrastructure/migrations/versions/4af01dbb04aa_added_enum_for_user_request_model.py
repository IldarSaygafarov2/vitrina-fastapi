"""added enum for user request model

Revision ID: 4af01dbb04aa
Revises: eb1d0e7a9257
Create Date: 2024-12-02 16:53:35.244760

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "4af01dbb04aa"
down_revision: Union[str, None] = "eb1d0e7a9257"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute("ALTER TABLE user_requests DROP COLUMN operation_type")
    op.execute("ALTER TABLE user_requests ADD COLUMN operation_type operationtype")
    # op.alter_column(
    #     "user_requests",
    #     "operation_type",
    #     existing_type=sa.VARCHAR(),
    #     type_=postgresql.ENUM("BUY", "RENT", name="operationtype"),
    #     nullable=True,
    # )
    op.execute(
        "CREATE TYPE objecttype AS ENUM('FLAT','COMMERCIAL','NEW_BUILDING','HOUSE')"
    )
    op.execute("ALTER TABLE user_requests DROP COLUMN object_type")
    op.execute("ALTER TABLE user_requests ADD COLUMN object_type objecttype")
    # op.alter_column(
    #     "user_requests",
    #     "object_type",
    #     existing_type=sa.VARCHAR(),
    #     type_=postgresql.ENUM(
    #         "FLAT", "COMMERCIAL", "NEW_BUILDING", "HOUSE", name="objecttype"
    #     ),
    #     nullable=True,
    # )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "user_requests",
        "object_type",
        existing_type=postgresql.ENUM(
            "FLAT", "COMMERCIAL", "NEW_BUILDING", "HOUSE", name="objecttype"
        ),
        type_=sa.VARCHAR(),
        nullable=False,
    )
    op.alter_column(
        "user_requests",
        "operation_type",
        existing_type=postgresql.ENUM("BUY", "RENT", name="operationtype"),
        type_=sa.VARCHAR(),
        nullable=False,
    )
    # ### end Alembic commands ###
