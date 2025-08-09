from __future__ import annotations

import uuid
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING, Annotated

import bcrypt
from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.templating import Jinja2Templates

from .admin import setup_admin
from .db import get_connection
from .parser import parse_chordpro
from .renderer import render_parsed_song
from .repositories.admin_users import create_admin, get_admin_by_email
from .repositories.songs import get_song_by_id, list_recent_songs, search_songs
from .settings import settings
from .transposer import compute_semitone_interval, transpose_chord_symbol

if TYPE_CHECKING:  # pragma: no cover
    from sqlalchemy.ext.asyncio import AsyncConnection


@asynccontextmanager
async def lifespan(_: FastAPI):
    if settings.admin_bootstrap_email and (
        settings.admin_bootstrap_password or settings.admin_bootstrap_password_hash
    ):
        async for conn in get_connection():
            existing = await get_admin_by_email(conn, settings.admin_bootstrap_email)
            if not existing:
                if settings.admin_bootstrap_password_hash:
                    pw_hash = settings.admin_bootstrap_password_hash.encode()
                else:
                    if settings.admin_bootstrap_password is None:
                        raise HTTPException(status_code=500, detail='Missing bootstrap password')
                    pw_hash = bcrypt.hashpw(
                        settings.admin_bootstrap_password.encode(),
                        bcrypt.gensalt(),
                    )
                await create_admin(
                    conn,
                    settings.admin_bootstrap_email,
                    pw_hash.decode() if isinstance(pw_hash, bytes) else pw_hash,
                )
            break
    yield


app = FastAPI(debug=settings.debug, lifespan=lifespan)
templates = Jinja2Templates(directory='app/templates')
app.mount('/static', StaticFiles(directory='static'), name='static')
setup_admin(app)


def parse_setlist_param(raw: str | None) -> list[tuple[uuid.UUID, str | None]]:
    """Parse setlist param into (id, key) pairs."""
    if not raw:
        return []
    items = []
    for part in raw.split(','):
        token = part.strip()
        if not token:
            continue
        if ':' in token:
            id_part, key_part = token.split(':', 1)
            items.append((uuid.UUID(id_part), key_part or None))
        else:
            items.append((uuid.UUID(token), None))
    return items


## removed deprecated startup event in favor of lifespan


@app.get('/health')
async def health() -> JSONResponse:
    """Return application health."""
    return JSONResponse({'status': 'ok'})


@app.get('/', response_class=HTMLResponse)
async def render_setlist(
    request: Request,
    s: Annotated[str | None, Query()] = None,
    dark: Annotated[int | None, Query()] = None,
    chords: Annotated[int | None, Query()] = 1,
    font: Annotated[str | None, Query()] = None,
    conn: Annotated[AsyncConnection, Depends(get_connection)] = Depends(get_connection),  # noqa: FAST002
) -> HTMLResponse:
    """Render one or many songs in a setlist."""
    pairs = parse_setlist_param(s)
    if not pairs:
        recent = await list_recent_songs(conn, limit=10)
        return templates.TemplateResponse(
            'search.html',
            {'request': request, 'results': recent, 'selected': [], 'query': ''},
        )
    blocks: list[str] = []
    for song_id, target_key in pairs:
        row = await get_song_by_id(conn, song_id)
        if not row or row.get('is_draft'):
            raise HTTPException(status_code=404, detail='Song not found')
        parsed = parse_chordpro(row['chordpro_content'])
        semitones = compute_semitone_interval(row.get('default_key'), target_key)
        for section in parsed.sections:
            for _idx, ch in enumerate(section.lines):
                ch.chords = [transpose_chord_symbol(c, semitones) if c else None for c in ch.chords]
        html = render_parsed_song(parsed, show_chords=bool(chords))
        title = str(row.get('translated_title'))
        artist = f' - {row["artist"]}' if row.get('artist') else ''
        header = f'<header class="song-header">{title}{artist}</header>'
        article = f'<article class="song">{header}{html}</article>'
        blocks.append(article)
    return templates.TemplateResponse(
        'song.html',
        {
            'request': request,
            'content': '<hr class="song-separator">'.join(blocks),
            'dark': bool(dark),
            'font': font or 'normal',
        },
    )


@app.get('/search', response_class=HTMLResponse)
async def search(
    request: Request,
    q: Annotated[str, Query()] = '',
    conn: Annotated[AsyncConnection, Depends(get_connection)] = Depends(get_connection),  # noqa: FAST002
) -> HTMLResponse:
    """Search and list songs."""
    results = await search_songs(conn, q) if q else []
    return templates.TemplateResponse(
        'search.html',
        {'request': request, 'results': results, 'selected': [], 'query': q},
    )
