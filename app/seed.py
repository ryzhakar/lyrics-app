from __future__ import annotations

import asyncio
from typing import TYPE_CHECKING

from .db import get_connection

if TYPE_CHECKING:  # pragma: no cover
    from sqlalchemy.ext.asyncio import AsyncConnection
from .repositories.songs import create_song


async def seed() -> None:
    """Insert sample songs for development."""
    async for conn in get_connection():
        await _seed_songs(conn)
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


if __name__ == '__main__':
    asyncio.run(seed())
