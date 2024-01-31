"""add user table

Revision ID: 34e3d9b306e7
Revises:
Create Date: 2024-01-31 09:07:50.357384

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "34e3d9b306e7"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), sa.Identity(always=False), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column(
            "created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user")),
    )


def downgrade() -> None:
    op.drop_table("user")
