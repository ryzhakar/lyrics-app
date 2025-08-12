from __future__ import annotations

import uuid
from contextlib import asynccontextmanager
from http import HTTPStatus
from typing import TYPE_CHECKING, Annotated

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.templating import Jinja2Templates

from .admin import setup_admin
from .db import get_connection
from .middleware import SecurityHeadersMiddleware
from .parser import parse_chordpro
from .renderer import render_parsed_song, render_stream_links
from .repositories.songs import get_song_by_id, list_recent_songs, search_songs
from .settings import settings
from .transposer import (
    compute_semitone_interval,
    prefer_sharps_for_key,
    transpose_chord_symbol,
)

if TYPE_CHECKING:  # pragma: no cover
    from sqlalchemy.ext.asyncio import AsyncConnection


@asynccontextmanager
async def lifespan(_: FastAPI):
    yield


app = FastAPI(debug=settings.debug, lifespan=lifespan)
templates = Jinja2Templates(directory='app/templates')
app.mount('/static', StaticFiles(directory='static'), name='static')
setup_admin(app)

# middleware
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)
if settings.gzip_min_length > 0:
    app.add_middleware(GZipMiddleware, minimum_size=settings.gzip_min_length)
if settings.allowed_hosts:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts)
if settings.cors_allow_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )
if settings.force_https:
    app.add_middleware(HTTPSRedirectMiddleware)
app.add_middleware(SecurityHeadersMiddleware)


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
            request,
            'search.html',
            {
                'results': recent,
                'selected': [],
                'query': '',
                'dark': bool(dark),
                'font': font or 'normal',
                'is_search': True,
            },
        )
    blocks: list[str] = []
    for song_id, target_key in pairs:
        row = await get_song_by_id(conn, song_id)
        if not row or row.get('is_draft'):
            raise HTTPException(status_code=404, detail='немає такого')
        try:
            parsed = parse_chordpro(row['chordpro_content'])
        except Exception as exc:
            raise HTTPException(status_code=400, detail='не вдалося розібрати') from exc
        semitones = compute_semitone_interval(row.get('default_key'), target_key)
        prefer_sharps = prefer_sharps_for_key(target_key)
        for section in parsed.sections:
            for _idx, ch in enumerate(section.lines):
                ch.chords = [
                    transpose_chord_symbol(c, semitones, prefer_sharps) if c else None
                    for c in ch.chords
                ]
        html = render_parsed_song(parsed, show_chords=bool(chords))
        title = str(row.get('translated_title'))
        artist = str(row.get('artist') or '')
        original = str(row.get('original_title') or '')
        # Center key (effective key after transpose)
        eff_key = target_key or row.get('default_key')
        links_html = render_stream_links(
            str(row.get('youtube_url') or '') or None,
            str(row.get('songlink_url') or '') or None,
        )
        left_stack_parts = [f'<div class="song-title">{title}</div>']
        if original:
            left_stack_parts.append(f'<div class="song-sub original">{original}</div>')
        if artist:
            left_stack_parts.append(f'<div class="song-sub artist">{artist}</div>')
        left_stack = '<div class="song-stack">' + ''.join(left_stack_parts) + '</div>'
        default_key_str = str(row.get('default_key') or '')
        eff_key_str = str(eff_key or '')
        key_base_attrs = (
            f'data-song-id="{song_id}" '
            f'data-default-key="{default_key_str}" '
            f'data-effective-key="{eff_key_str}"'
        )
        up_btn = (
            '<button type="button" class="icon-btn key-btn transpose-btn" '
            'data-dir="up" aria-label="Transpose up" title="Transpose up">'
            '<span class="icon icon-chev-up" aria-hidden="true"></span>'
            '</button>'
        )
        down_btn = (
            '<button type="button" class="icon-btn key-btn transpose-btn" '
            'data-dir="down" aria-label="Transpose down" title="Transpose down">'
            '<span class="icon icon-chev-down" aria-hidden="true"></span>'
            '</button>'
        )
        key_label = f'<div class="key-label">Тональність: {eff_key or "&nbsp;"}</div>'
        key_html = (
            f'<div class="song-key" {key_base_attrs}>{up_btn}{key_label}{down_btn}</div>'
            if bool(chords)
            else ''
        )
        header = (
            '<header class="song-header">'
            f'{left_stack}'
            f'{key_html}'
            f'<div class="song-links">{links_html}</div>'
            '</header>'
        )
        article = f'<article class="song">{header}<div class="song-body">{html}</div></article>'
        blocks.append(article)
    return templates.TemplateResponse(
        request,
        'song.html',
        {
            'content': '<hr class="song-separator">'.join(blocks),
            'dark': bool(dark),
            'font': font or 'normal',
            'chords': bool(chords),
            'is_search': False,
        },
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == HTTPStatus.NOT_FOUND:
        return templates.TemplateResponse(
            request,
            '404.html',
            {
                'dark': bool((request.query_params.get('dark') or '0') == '1'),
                'font': request.query_params.get('font') or 'normal',
                'is_search': True,
            },
            status_code=HTTPStatus.NOT_FOUND,
        )
    return JSONResponse({'detail': exc.detail}, status_code=exc.status_code)


@app.get('/search', response_class=HTMLResponse)
async def search(
    request: Request,
    q: Annotated[str, Query()] = '',
    dark: Annotated[int | None, Query()] = None,
    font: Annotated[str | None, Query()] = None,
    conn: Annotated[AsyncConnection, Depends(get_connection)] = Depends(get_connection),  # noqa: FAST002
) -> HTMLResponse:
    """Search and list songs."""
    results = await search_songs(conn, q, limit=200) if q else []
    return templates.TemplateResponse(
        request,
        'search.html',
        {
            'results': results,
            'selected': [],
            'query': q,
            'dark': bool(dark),
            'font': font or 'normal',
            'is_search': True,
        },
    )
