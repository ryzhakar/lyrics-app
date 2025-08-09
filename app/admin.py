from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:  # pragma: no cover
    from fastapi import Request
from sqladmin import Admin, ModelView

from .db import engine
from .models import AdminUserModel, SongModel
from .parser import parse_chordpro


class SongAdmin(ModelView):
    """Configure admin for songs."""

    category = 'Content'
    icon = 'fa-solid fa-music'
    model = SongModel

    async def on_model_change(
        self,
        data: dict[str, Any],
        model: SongModel,
        is_created: bool,
        request: Request,
    ) -> None:
        """Validate ChordPro before saving."""
        _ = (is_created, request)
        content = data.get('chordpro_content') or model.chordpro_content
        parse_chordpro(content)


class AdminUserAdmin(ModelView):
    """Configure admin for users."""

    category = 'Users'
    icon = 'fa-solid fa-user'
    model = AdminUserModel


def setup_admin(app: Any) -> Admin:
    """Set up SQLAdmin with views."""
    admin = Admin(app=app, engine=engine.sync_engine)
    admin.add_view(SongAdmin)
    admin.add_view(AdminUserAdmin)
    return admin
