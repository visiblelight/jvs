"""add_short_name_to_tick_tasks

Revision ID: f1a2b3c4d5e6
Revises: 0b262c5f0426
Create Date: 2026-04-10 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'f1a2b3c4d5e6'
down_revision: Union[str, None] = '0b262c5f0426'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        'tick_tasks',
        sa.Column('short_name', sa.String(10), nullable=False, server_default='')
    )


def downgrade() -> None:
    op.drop_column('tick_tasks', 'short_name')
