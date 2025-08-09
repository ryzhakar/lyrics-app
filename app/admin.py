from __future__ import annotations

from typing import TYPE_CHECKING, Any, ClassVar

if TYPE_CHECKING:  # pragma: no cover
    from fastapi import Request
from sqladmin import Admin, ModelView
from sqlalchemy import create_engine

from .auth import AdminAuth
from .models import AdminUserModel, SongModel
from .parser import parse_chordpro
from .settings import settings
from .transposer import NOTE_TO_SEMITONE


class SongAdmin(ModelView, model=SongModel):
    """Configure admin for songs."""

    category = 'Content'
    icon = 'fa-solid fa-music'
    column_list: ClassVar[list[str]] = ['id', 'translated_title', 'artist', 'is_draft']
    form_columns: ClassVar[list[str]] = [
        'translated_title',
        'original_title',
        'artist',
        'chordpro_content',
        'default_key',
        'youtube_url',
        'songlink_url',
        'is_draft',
    ]

    async def on_model_change(
        self,
        data: dict[str, Any],
        model: SongModel,
        is_created: bool,
        request: Request,
    ) -> None:
        """Validate ChordPro before saving."""
        _ = (is_created, request)
        raw = data.get('chordpro_content') if 'chordpro_content' in data else model.chordpro_content
        content: str = str(raw)
        parse_chordpro(content)
        dk_raw = (
            data.get('default_key')
            if 'default_key' in data
            else getattr(model, 'default_key', None)
        )
        dk = str(dk_raw) if dk_raw is not None else ''
        if not dk:
            raise ValueError('default_key is required')
        root = dk.rstrip('m')
        if root not in NOTE_TO_SEMITONE:
            raise ValueError('default_key must be a valid key (e.g., C, F#, Eb, Em)')


class AdminUserAdmin(ModelView, model=AdminUserModel):
    """Configure admin for users."""

    category = 'Users'
    icon = 'fa-solid fa-user'
    column_list: ClassVar[list[str]] = ['id', 'email']
    form_columns: ClassVar[list[str]] = ['email', 'password_hash']


def _sync_db_url(url: str) -> str:
    """Normalize async pg URL to psycopg sync driver."""
    if '+asyncpg' in url:
        return url.replace('+asyncpg', '+psycopg')
    if url.startswith('postgresql://'):
        return url.replace('postgresql://', 'postgresql+psycopg://', 1)
    return url


def setup_admin(app: Any) -> Admin:
    """Set up SQLAdmin with views."""
    sync_engine = create_engine(_sync_db_url(settings.database_url), pool_pre_ping=True)
    admin = Admin(
        app=app,
        engine=sync_engine,
        authentication_backend=AdminAuth(settings.secret_key),
    )
    admin.add_view(SongAdmin)
    admin.add_view(AdminUserAdmin)
    return admin
