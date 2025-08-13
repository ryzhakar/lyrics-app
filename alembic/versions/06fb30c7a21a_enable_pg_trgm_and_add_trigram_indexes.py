"""
Enable pg_trgm and add trigram indexes.

Revision ID: 06fb30c7a21a
Revises: 20250209_000001
Create Date: 2025-08-13 03:23:19.136645

"""

from __future__ import annotations

from alembic import op

revision = '06fb30c7a21a'
down_revision = '20250209_000001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Enable pg_trgm and create recommended trigram/GIN indexes."""
    op.execute('CREATE EXTENSION IF NOT EXISTS pg_trgm')
    # Trigram GIN indexes for better fuzzy search on title and artist
    op.execute(
        (
            'CREATE INDEX IF NOT EXISTS songs_title_trgm '
            'ON songs USING gin (translated_title gin_trgm_ops)'
        ),
    )
    op.execute(
        'CREATE INDEX IF NOT EXISTS songs_artist_trgm ON songs USING gin (artist gin_trgm_ops)',
    )
    # If search_vector column exists, ensure a GIN index on it
    op.execute(
        'CREATE INDEX IF NOT EXISTS songs_search_vector_gin ON songs USING gin (search_vector)',
    )


def downgrade() -> None:
    """Drop created indexes (keep extension for other deps)."""
    op.execute('DROP INDEX IF EXISTS songs_search_vector_gin')
    op.execute('DROP INDEX IF EXISTS songs_artist_trgm')
    op.execute('DROP INDEX IF EXISTS songs_title_trgm')
