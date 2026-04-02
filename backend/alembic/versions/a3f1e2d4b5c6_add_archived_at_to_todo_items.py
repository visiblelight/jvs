"""add_archived_at_to_todo_items

Revision ID: a3f1e2d4b5c6
Revises: 95c8c64987fd
Create Date: 2026-04-02 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a3f1e2d4b5c6'
down_revision: Union[str, None] = '95c8c64987fd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('todo_items', sa.Column('archived_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    op.drop_column('todo_items', 'archived_at')
