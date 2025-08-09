"""
Create core tables and search triggers.

Revision ID: 20250101_000000
Revises:
Create Date: 2025-01-01 00:00:00

"""

from __future__ import annotations

import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op as alembic_op

revision = '20250101_000000'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    alembic_op.execute('CREATE EXTENSION IF NOT EXISTS pgcrypto')
    alembic_op.execute('CREATE EXTENSION IF NOT EXISTS pg_trgm')
    alembic_op.create_table(
        'songs',
        sa.Column(
            'id',
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text('gen_random_uuid()'),
        ),
        sa.Column('original_title', sa.String(length=255), nullable=True),
        sa.Column('translated_title', sa.String(length=255), nullable=False),
        sa.Column('artist', sa.String(length=255), nullable=True),
        sa.Column('chordpro_content', sa.Text(), nullable=False),
        sa.Column('default_key', sa.String(length=3), nullable=True),
        sa.Column('youtube_url', sa.String(length=500), nullable=True),
        sa.Column('songlink_url', sa.String(length=500), nullable=True),
        sa.Column('is_draft', sa.Boolean(), server_default=sa.text('false'), nullable=False),
        sa.Column('search_vector', postgresql.TSVECTOR(), nullable=True),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    alembic_op.create_index('ix_translated_title', 'songs', ['translated_title'])
    alembic_op.create_index('ix_artist', 'songs', ['artist'])
    alembic_op.create_index('ix_songs_created_at_desc', 'songs', [sa.text('created_at DESC')])
    alembic_op.create_index(
        'ix_songs_search_vector',
        'songs',
        ['search_vector'],
        unique=False,
        postgresql_using='gin',
    )

    alembic_op.create_table(
        'admin_users',
        sa.Column(
            'id',
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text('gen_random_uuid()'),
        ),
        sa.Column('email', sa.String(length=320), nullable=False, unique=True),
        sa.Column('password_hash', sa.String(length=200), nullable=False),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            'updated_at',
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )

    alembic_op.execute(
        """
        CREATE OR REPLACE FUNCTION songs_update_search_vector() RETURNS trigger AS $$
        DECLARE
          lyrics text;
        BEGIN
          lyrics := NEW.chordpro_content;
          lyrics := regexp_replace(lyrics, '\\[[^\\]]+\\]', '', 'g');
          lyrics := regexp_replace(lyrics, '\\{start_of_section:[^}]+\\}', '', 'gi');
          lyrics := regexp_replace(lyrics, '\\{end_of_section\\}', '', 'gi');
          NEW.search_vector :=
            setweight(to_tsvector('simple', coalesce(NEW.translated_title, '')), 'A') ||
            setweight(to_tsvector('simple', coalesce(NEW.original_title, '')), 'B') ||
            setweight(to_tsvector('simple', coalesce(NEW.artist, '')), 'B') ||
            setweight(to_tsvector('simple', coalesce(lyrics, '')), 'C');
          RETURN NEW;
        END
        $$ LANGUAGE plpgsql;
        """,
    )
    alembic_op.execute(
        """
        CREATE TRIGGER songs_search_vector_trigger
        BEFORE INSERT OR UPDATE OF translated_title, original_title, artist, chordpro_content
        ON songs
        FOR EACH ROW EXECUTE FUNCTION songs_update_search_vector();
        """,
    )


def downgrade() -> None:
    alembic_op.execute('DROP TRIGGER IF EXISTS songs_search_vector_trigger ON songs')
    alembic_op.execute('DROP FUNCTION IF EXISTS songs_update_search_vector')
    alembic_op.drop_table('admin_users')
    alembic_op.drop_index('ix_songs_search_vector', table_name='songs')
    alembic_op.drop_index('ix_songs_created_at_desc', table_name='songs')
    alembic_op.drop_index('ix_artist', table_name='songs')
    alembic_op.drop_index('ix_translated_title', table_name='songs')
    alembic_op.drop_table('songs')
