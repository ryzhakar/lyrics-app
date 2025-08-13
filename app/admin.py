from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING, Any, ClassVar

import bcrypt

if TYPE_CHECKING:  # pragma: no cover
    from fastapi import Request
from sqladmin import Admin, ModelView
from sqladmin.application import action
from sqlalchemy import create_engine
from wtforms import PasswordField, TextAreaField

from .auth import AdminAuth
from .models import AdminUserModel, SongModel
from .parser import parse_chordpro
from .settings import settings
from .transposer import NOTE_TO_SEMITONE


class SongAdmin(ModelView, model=SongModel):
    """Configure admin for songs."""

    category = ''
    icon = 'fa-solid fa-music'
    column_list: ClassVar[list[str]] = ['translated_title', 'is_draft']
    column_display_pk: ClassVar[bool] = False
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
    form_overrides: ClassVar[dict[str, Any]] = {'chordpro_content': TextAreaField}
    form_widget_args: ClassVar[dict[str, dict[str, Any]]] = {
        'chordpro_content': {
            'rows': 30,
            'style': (
                'min-height: 74vh; '
                'width: 100%; max-width: none; display: block; box-sizing: border-box; '
                'font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, '
                "'Liberation Mono', 'Courier New', monospace; "
                'font-size: 14px; line-height: 1.35;'
            ),
            'spellcheck': 'false',
            'autocapitalize': 'off',
            'autocomplete': 'off',
            'autocorrect': 'off',
            'wrap': 'off',
            'class': 'chordpro-textarea',
        },
    }
    create_template: ClassVar[str] = 'sqladmin/create_ext.html'
    edit_template: ClassVar[str] = 'sqladmin/edit_ext.html'
    list_template: ClassVar[str] = 'sqladmin/list_ext.html'
    details_template: ClassVar[str] = 'sqladmin/details_ext.html'

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

    category = ''
    icon = 'fa-solid fa-user'
    page_size: ClassVar[int] = 20
    column_list: ClassVar[list[str]] = ['email']
    column_display_pk: ClassVar[bool] = False
    form_excluded_columns: ClassVar[list[str]] = ['password_hash', 'created_at', 'updated_at']
    form_extra_fields: ClassVar[dict[str, Any]] = {
        'password': PasswordField('New password', render_kw={'autocomplete': 'new-password'}),
    }
    can_create: ClassVar[bool] = True
    can_edit: ClassVar[bool] = True
    can_delete: ClassVar[bool] = True
    create_template: ClassVar[str] = 'sqladmin/create_ext.html'
    edit_template: ClassVar[str] = 'sqladmin/edit_ext.html'
    list_template: ClassVar[str] = 'sqladmin/list_ext.html'
    details_template: ClassVar[str] = 'sqladmin/details_ext.html'

    async def scaffold_form(self, rules: list[str] | None = None):  # type: ignore[override]
        base = await super().scaffold_form(rules)
        form_cls = type(
            'AdminUserForm',
            (base,),
            {
                'password': PasswordField(
                    'New password',
                    render_kw={'autocomplete': 'new-password'},
                ),
            },
        )
        return form_cls

    async def on_model_change(
        self,
        data: dict[str, Any],
        model: AdminUserModel,  # noqa: ARG002
        is_created: bool,
        request: Request,
    ) -> None:
        """Hash password field on create/update and never persist raw value."""
        _ = (request,)
        raw_pw = data.get('password') if data and 'password' in data else None
        if is_created and not raw_pw:
            raise ValueError('password is required')
        if raw_pw:
            hashed = bcrypt.hashpw(str(raw_pw).encode(), bcrypt.gensalt()).decode()
            data['password_hash'] = hashed
        if data and 'password' in data:
            data.pop('password')

    @action(
        name='reset-password',
        label='Reset password',
        confirmation_message='Generate a new random password and display it once?',
        add_in_detail=True,
        add_in_list=True,
    )
    async def reset_password(self, request: Any) -> Any:
        """Reset selected admins' passwords and show new ones once."""
        from secrets import token_urlsafe

        pks_raw = request.query_params.get('pks') or ''
        pks = [pk for pk in pks_raw.split(',') if pk]
        if not pks:
            return await self.templates.TemplateResponse(
                request,
                'sqladmin/action_result.html',
                {'model_view': self, 'title': 'Reset password', 'items': []},
            )
        rows: list[dict[str, str]] = []
        for pk in pks:
            obj = await self.get_object_for_delete(pk)
            if not obj:
                continue
            new_pw = token_urlsafe(12)
            hashed = bcrypt.hashpw(new_pw.encode(), bcrypt.gensalt()).decode()
            await self.update_model(request, pk=pk, data={'password_hash': hashed})
            email = getattr(obj, 'email', '')
            rows.append({'email': str(email), 'password': new_pw})
        return await self.templates.TemplateResponse(
            request,
            'sqladmin/action_result.html',
            {'model_view': self, 'title': 'Reset password', 'items': rows},
        )


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
        templates_dir=str(Path(__file__).parent / 'templates'),
    )
    # Add song list as first view so admin loads with songs by default
    admin.add_view(SongAdmin)
    admin.add_view(AdminUserAdmin)
    return admin
