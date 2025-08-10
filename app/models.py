from __future__ import annotations

from typing import ClassVar
from uuid import UUID  # noqa: TC003

from sqlalchemy.orm import registry

from .db import admin_users as admin_users_table
from .db import songs as songs_table

mapper_registry: registry = registry()


@mapper_registry.mapped
class SongModel:
    """Represent a song for admin views."""

    __table__ = songs_table
    __allow_unmapped__ = True

    id: ClassVar[UUID]
    original_title: ClassVar[str | None]
    translated_title: ClassVar[str]
    artist: ClassVar[str | None]
    chordpro_content: ClassVar[str]
    default_key: ClassVar[str]
    youtube_url: ClassVar[str | None]
    songlink_url: ClassVar[str | None]
    is_draft: ClassVar[bool]


@mapper_registry.mapped
class AdminUserModel:
    """Represent an admin user for admin views."""

    __table__ = admin_users_table
    __allow_unmapped__ = True

    id: ClassVar[UUID]
    email: ClassVar[str]
    password_hash: ClassVar[str]
