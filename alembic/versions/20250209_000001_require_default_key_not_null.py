"""
Require default_key to be NOT NULL.

Revision ID: 20250209_000001
Revises: 20250101_000000
Create Date: 2025-02-09 00:00:01
"""

from __future__ import annotations

from alembic import op as alembic_op

revision = '20250209_000001'
down_revision = '20250101_000000'
branch_labels = None
depends_on = None


def upgrade() -> None:
    alembic_op.execute("UPDATE songs SET default_key = 'C' WHERE default_key IS NULL")
    alembic_op.alter_column('songs', 'default_key', nullable=False)


def downgrade() -> None:
    alembic_op.alter_column('songs', 'default_key', nullable=True)
