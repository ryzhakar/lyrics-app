from __future__ import annotations

import uuid

import pytest
from sqlalchemy import insert, select

from app.db import songs
from app.main import app, parse_setlist_param


def test_parse_setlist_param_parses_mixed() -> None:
    id1 = uuid.uuid4()
    id2 = uuid.uuid4()
    parsed = parse_setlist_param(f'{id1}:G,{id2}')
    assert parsed == [(id1, 'G'), (id2, None)]


from typing import Any


@pytest.mark.asyncio
async def test_health_endpoint(client: Any) -> None:
    res = await client.get('/health')
    assert res.status_code == 200
    assert res.json()['status'] == 'ok'


@pytest.mark.asyncio
async def test_search_ordering_prioritizes_title_prefix(client: Any) -> None:
    from sqlalchemy.ext.asyncio import AsyncConnection
    from app.db import engine

    async with engine.begin() as db_conn:  # type: ignore[assignment]
        assert isinstance(db_conn, AsyncConnection)
        await db_conn.execute(
            insert(songs).values(
                translated_title='Amazing Grace',
                artist='John Newton',
                chordpro_content='[C]Amazing',
                default_key='C',
                is_draft=False,
            ),
        )
        await db_conn.execute(
            insert(songs).values(
                translated_title='Grace Song',
                artist='Amazing Artist',
                chordpro_content='lyrics amazing',
                default_key='C',
                is_draft=False,
            ),
        )

    r = await client.get('/search?q=Amazing')
    assert r.status_code == 200
    body = r.text
    first_idx = body.find('Amazing Grace')
    second_idx = body.find('Grace Song')
    assert first_idx != -1 and second_idx != -1
    assert first_idx < second_idx


@pytest.mark.asyncio
async def test_search_and_list_exclude_drafts(client: Any) -> None:
    from sqlalchemy.ext.asyncio import AsyncConnection
    from app.db import engine

    async with engine.begin() as db_conn:  # type: ignore[assignment]
        assert isinstance(db_conn, AsyncConnection)
        await db_conn.execute(
            insert(songs).values(
                translated_title='Amazing Grace',
                artist='John Newton',
                chordpro_content='[C]Amazing',
                default_key='C',
                is_draft=False,
            ),
        )
        await db_conn.execute(
            insert(songs).values(
                translated_title='Draft Song',
                artist='Hidden',
                chordpro_content='[C]Hidden',
                default_key='C',
                is_draft=True,
            ),
        )

    res = await client.get('/')
    assert res.status_code == 200
    body = res.text
    assert 'Amazing Grace' in body
    assert 'Draft Song' not in body

    res2 = await client.get('/search?q=amazing')
    assert res2.status_code == 200
    assert 'Amazing Grace' in res2.text
    assert 'Draft Song' not in res2.text


@pytest.mark.asyncio
async def test_setlist_route_renders_and_applies_flags(client: Any) -> None:
    from sqlalchemy.ext.asyncio import AsyncConnection
    from app.db import get_connection

    song_id = None
    async for db_conn in get_connection():  # type: ignore[assignment]
        assert isinstance(db_conn, AsyncConnection)
        result = await db_conn.execute(
            insert(songs)
            .values(
                translated_title='Test Song',
                artist=None,
                chordpro_content='[C]Amazing',
                default_key='C',
                is_draft=False,
            )
            .returning(songs.c.id)
        )
        song_id = result.scalar_one()
        await db_conn.commit()
        break

    assert song_id is not None
    res = await client.get(f'/?s={song_id}:D&chords=0&dark=1&font=large')
    assert res.status_code == 200
    html = res.text
    assert '<article class="song">' in html
    assert '<pre class="chords">' not in html
    assert 'song-container' in html
    # dark mode class is applied
    assert ' class="dark ' in html


@pytest.mark.asyncio
async def test_setlist_404s_on_draft(client: Any) -> None:
    from sqlalchemy.ext.asyncio import AsyncConnection
    from app.db import engine

    async with engine.begin() as db_conn:  # type: ignore[assignment]
        assert isinstance(db_conn, AsyncConnection)
        result = await db_conn.execute(
            insert(songs)
            .values(
                translated_title='Draft Song',
                chordpro_content='[C]Hidden',
                default_key='C',
                is_draft=True,
            )
            .returning(songs.c.id)
        )
        song_id = result.scalar_one()

    res = await client.get(f'/?s={song_id}:C')
    assert res.status_code == 404


@pytest.mark.asyncio
async def test_repository_include_drafts_queries() -> None:
    from sqlalchemy.ext.asyncio import AsyncConnection
    from app.db import engine

    async with engine.begin() as db_conn:  # type: ignore[assignment]
        assert isinstance(db_conn, AsyncConnection)
        await db_conn.execute(
            insert(songs).values(
                translated_title='Public',
                artist='A',
                chordpro_content='text',
                default_key='C',
                is_draft=False,
            ),
        )
        await db_conn.execute(
            insert(songs).values(
                translated_title='Private',
                artist='B',
                chordpro_content='text',
                default_key='C',
                is_draft=True,
            ),
        )
        rows = (await db_conn.execute(select(songs))).mappings().all()
        assert any(r['translated_title'] == 'Public' for r in rows)
        assert any(r['translated_title'] == 'Private' for r in rows)
