from __future__ import annotations

from uuid import UUID  # noqa: TC003

from sqlalchemy.orm import registry

from .db import admin_users as admin_users_table
from .db import songs as songs_table

mapper_registry: registry = registry()


@mapper_registry.mapped
class SongModel:
    """Represent a song for admin views."""

    __table__ = songs_table

    id: UUID
    original_title: str | None
    translated_title: str
    artist: str | None
    chordpro_content: str
    default_key: str | None
    youtube_url: str | None
    songlink_url: str | None
    is_draft: bool


@mapper_registry.mapped
class AdminUserModel:
    """Represent an admin user for admin views."""

    __table__ = admin_users_table

    id: UUID
    email: str
    password_hash: str
