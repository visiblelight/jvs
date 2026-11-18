"""Add revocable login sessions and user authentication version.

Revision ID: c026a1b2c3d4
Revises: a2b3c4d5e6f7
"""
from alembic import op
import sqlalchemy as sa

revision = "c026a1b2c3d4"
down_revision = "a2b3c4d5e6f7"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("users", sa.Column("token_version", sa.Integer(), nullable=False, server_default="0"))
    op.create_table(
        "auth_sessions",
        sa.Column("id", sa.String(36), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_hash", sa.String(64), nullable=False),
        sa.Column("previous_token_hash", sa.String(64), nullable=True),
        sa.Column("previous_valid_until", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("last_used_at", sa.DateTime(), nullable=False),
        sa.Column("idle_expires_at", sa.DateTime(), nullable=False),
        sa.Column("absolute_expires_at", sa.DateTime(), nullable=False),
        sa.Column("revoked_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_auth_sessions_user_id", "auth_sessions", ["user_id"])
    op.create_index("ix_auth_sessions_absolute_expires_at", "auth_sessions", ["absolute_expires_at"])


def downgrade():
    op.drop_table("auth_sessions")
    op.drop_column("users", "token_version")
