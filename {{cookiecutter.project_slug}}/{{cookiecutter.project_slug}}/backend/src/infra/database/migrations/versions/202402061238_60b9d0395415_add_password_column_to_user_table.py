"""add password column to user table

Revision ID: 60b9d0395415
Revises: 34e3d9b306e7
Create Date: 2024-02-06 12:38:28.274429

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "60b9d0395415"
down_revision: Union[str, None] = "34e3d9b306e7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("user", sa.Column("password", sa.LargeBinary(), nullable=False))


def downgrade() -> None:
    op.drop_column("user", "password")
