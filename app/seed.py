from __future__ import annotations

import asyncio
import secrets
from pathlib import Path
from typing import TYPE_CHECKING

import bcrypt

from .db import get_connection

if TYPE_CHECKING:  # pragma: no cover
    from sqlalchemy.ext.asyncio import AsyncConnection
from .repositories.admin_users import create_admin, get_admin_by_email
from .repositories.songs import create_song
from .settings import settings


async def seed() -> None:
    """Insert sample songs for development."""
    async for conn in get_connection():
        await _seed_songs(conn)
        await _seed_admin(conn)
        _ensure_env()
        break


async def _seed_songs(conn: AsyncConnection) -> None:
    """Insert sample songs if none exist."""
    song1 = {
        'translated_title': 'Amazing Grace',
        'artist': 'John Newton',
        'chordpro_content': '[C]Amazing gr[G]ace how [Am]sweet the [F]sound',
        'default_key': 'C',
        'is_draft': False,
    }
    song2 = {
        'translated_title': 'How Great Thou Art',
        'artist': 'Carl Boberg',
        'chordpro_content': (
            '{start_of_section: Verse}\n'
            '[C]O Lord my [F]God, when [C]I in [G]awesome wonder\n'
            '{end_of_section}'
        ),
        'default_key': 'C',
        'is_draft': False,
    }
    await create_song(conn, song1)
    await create_song(conn, song2)


async def _seed_admin(conn: AsyncConnection) -> None:
    """Create initial admin user if missing and stage creds for env."""
    email = 'admin@localhost'
    existing = await get_admin_by_email(conn, email)
    if existing:
        return
    password = secrets.token_urlsafe(16)
    pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
    await create_admin(conn, email, pw_hash)
    _write_env_vars(
        {
            'ADMIN_BOOTSTRAP_EMAIL': email,
            'ADMIN_BOOTSTRAP_PASSWORD': password,
            'ADMIN_BOOTSTRAP_PASSWORD_HASH': pw_hash,
        },
    )


def _ensure_env() -> None:
    """Generate base .env with secrets if missing keys."""
    defaults = {
        'DATABASE_URL': settings.database_url,
        'SECRET_KEY': secrets.token_urlsafe(32),
        'DEBUG': 'false',
    }
    _write_env_vars(defaults)


def _write_env_vars(values: dict[str, str]) -> None:
    """Write missing environment variables to .env."""
    env_path = Path('.env')
    current: dict[str, str] = {}
    if env_path.exists():
        with env_path.open('r', encoding='utf-8') as f:
            for line_raw in f:
                ln = line_raw.strip()
                if not ln or ln.startswith('#') or '=' not in ln:
                    continue
                k, v = ln.split('=', 1)
                current[k.strip()] = v.strip()
    updated = dict(current)
    for k, v in values.items():
        if k not in updated or not updated[k]:
            updated[k] = v
    if updated == current:
        return
    lines = [f'{k}={v}\n' for k, v in updated.items()]
    tmp_path = env_path.with_suffix('.env.tmp')
    with tmp_path.open('w', encoding='utf-8') as f:
        f.writelines(lines)
    tmp_path.replace(env_path)


if __name__ == '__main__':
    asyncio.run(seed())
