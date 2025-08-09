from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Column, DateTime, Index, MetaData, String, Table, Text, func, text
from sqlalchemy.dialects.postgresql import TSVECTOR, UUID
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from .settings import settings


def _build_metadata() -> MetaData:
    """Build metadata with naming conventions."""
    return MetaData(
        naming_convention={
            'ix': 'ix_%(column_0_label)s',
            'uq': 'uq_%(table_name)s_%(column_0_name)s',
            'ck': 'ck_%(table_name)s_%(constraint_name)s',
            'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
            'pk': 'pk_%(table_name)s',
        },
    )


metadata = _build_metadata()


songs = Table(
    'songs',
    metadata,
    Column('id', UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')),
    Column('original_title', String(255), nullable=True),
    Column('translated_title', String(255), nullable=False, index=True),
    Column('artist', String(255), nullable=True, index=True),
    Column('chordpro_content', Text, nullable=False),
    Column('default_key', String(3), nullable=True),
    Column('youtube_url', String(500), nullable=True),
    Column('songlink_url', String(500), nullable=True),
    Column('is_draft', Boolean, nullable=False, server_default=text('false')),
    Column('search_vector', TSVECTOR, nullable=True),
    Column('created_at', DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column(
        'updated_at',
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    ),
    Index('ix_songs_created_at_desc', text('created_at DESC')),
)


admin_users = Table(
    'admin_users',
    metadata,
    Column('id', UUID(as_uuid=True), primary_key=True, server_default=text('gen_random_uuid()')),
    Column('email', String(320), nullable=False, unique=True),
    Column('password_hash', String(200), nullable=False),
    Column('created_at', DateTime(timezone=True), nullable=False, server_default=func.now()),
    Column(
        'updated_at',
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    ),
)


def create_engine() -> AsyncEngine:
    """Create an async SQLAlchemy engine."""
    return create_async_engine(settings.database_url, pool_pre_ping=True, future=True)


engine: AsyncEngine = create_engine()


if TYPE_CHECKING:  # pragma: no cover
    from collections.abc import AsyncGenerator

    from sqlalchemy.ext.asyncio import AsyncConnection


async def get_connection() -> AsyncGenerator[AsyncConnection, None]:
    """Yield an async database connection."""
    async with engine.connect() as conn:
        yield conn
