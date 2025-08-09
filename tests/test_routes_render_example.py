from __future__ import annotations

import uuid

import pytest
from sqlalchemy import insert

from app.db import songs


@pytest.mark.asyncio
async def test_route_renders_example_file(client):  # type: ignore[no-untyped-def]
    # Insert a song row with example content inline to avoid external file dependency
    from sqlalchemy.ext.asyncio import AsyncConnection
    from app.db import engine

    raw = (
        '{start_of_section: Куплет 1}\n'
        '[B]Тату мо[A]єму\n'
        'на[E]лежить Усесвіт\n'
        'і [Em6]подих оцей мій:\n'
        '[G#m7]о — о — [Emaj9]о.\n'
        '{end_of_section}\n'
    )
    async with engine.begin() as conn:  # type: ignore[assignment]
        assert isinstance(conn, AsyncConnection)
        res = await conn.execute(
            insert(songs)
            .values(
                translated_title='Example',
                artist='Test',
                chordpro_content=raw,
                default_key='E',
                is_draft=False,
            )
            .returning(songs.c.id)
        )
        song_id = res.scalar_one()

    # Render via route with chords on
    r = await client.get(f'/?s={song_id}:E&chords=1')
    assert r.status_code == 200
    html = r.text
    assert '<article class="song">' in html
    assert '<h3 class="section-header">Куплет 1</h3>' in html
    assert 'Тату моєму' in html
    assert 'о — о — о' in html
    # chords from the first line appear somewhere (exact alignment unit-tested elsewhere)
    assert 'B' in html and 'A' in html and 'E' in html
