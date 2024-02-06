"""ensure the user.user_id and user.email are unique

Revision ID: 17c33d2e56fe
Revises: 60b9d0395415
Create Date: 2024-02-06 13:27:47.518142

"""
from typing import Sequence, Union

from alembic import op


revision: str = '17c33d2e56fe'
down_revision: Union[str, None] = '60b9d0395415'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_unique_constraint(op.f('uq_user_email'), 'user', ['email'])
    op.create_unique_constraint(op.f('uq_user_user_id'), 'user', ['user_id'])


def downgrade() -> None:
    op.drop_constraint(op.f('uq_user_user_id'), 'user', type_='unique')
    op.drop_constraint(op.f('uq_user_email'), 'user', type_='unique')
