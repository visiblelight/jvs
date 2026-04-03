"""add_purged_at_to_todo_items

Revision ID: b4e2f3a1c8d9
Revises: a3f1e2d4b5c6
Create Date: 2026-04-03 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'b4e2f3a1c8d9'
down_revision: Union[str, None] = 'a3f1e2d4b5c6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('todo_items', sa.Column('purged_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column('todo_items', 'purged_at')
