"""add_tick_tables

Revision ID: 0b262c5f0426
Revises: b3c5320696bc
Create Date: 2026-04-06 11:20:11.297882

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '0b262c5f0426'
down_revision: Union[str, None] = 'b3c5320696bc'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'tick_tasks',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('frequency', sa.String(10), nullable=False),
        sa.Column('frequency_config', sa.Text(), nullable=False, server_default='{}'),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('enable_quality', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('enable_points', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('points_rule', sa.Text(), nullable=False, server_default='[]'),
        sa.Column('is_archived', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_tick_tasks_user_id', 'tick_tasks', ['user_id'])

    op.create_table(
        'tick_logs',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('ticked_at', sa.DateTime(), nullable=False),
        sa.Column('period_key', sa.String(10), nullable=False),
        sa.Column('quality', sa.Integer(), nullable=True),
        sa.Column('note', sa.Text(), nullable=True),
        sa.Column('points_earned', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['task_id'], ['tick_tasks.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('task_id', 'period_key', name='uq_tick_log_task_period'),
    )
    op.create_index('ix_tick_logs_user_id', 'tick_logs', ['user_id'])
    op.create_index('ix_tick_logs_task_id', 'tick_logs', ['task_id'])

    # 给所有已有非超管活跃用户授予 tick 板块权限
    op.execute(
        "INSERT INTO user_modules (user_id, module_key, granted_at) "
        "SELECT u.id, 'tick', CURRENT_TIMESTAMP FROM users u "
        "WHERE u.is_superuser = 0 AND u.is_active = 1 "
        "AND NOT EXISTS (SELECT 1 FROM user_modules um WHERE um.user_id = u.id AND um.module_key = 'tick')"
    )


def downgrade() -> None:
    op.drop_table('tick_logs')
    op.drop_table('tick_tasks')
    op.execute("DELETE FROM user_modules WHERE module_key = 'tick'")
