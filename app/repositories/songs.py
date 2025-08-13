from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import and_, case, func, insert, literal, or_, select, text

from app.db import songs

if TYPE_CHECKING:  # pragma: no cover
    from sqlalchemy import Select
    from sqlalchemy.engine import Result
    from sqlalchemy.ext.asyncio import AsyncConnection


async def create_song(conn: AsyncConnection, values: dict[str, Any]) -> Any:
    """Create a song and return row."""
    stmt = insert(songs).values(values).returning(songs)
    res: Result = await conn.execute(stmt)
    return res.mappings().one()


async def get_song_by_id(conn: AsyncConnection, song_id: Any) -> dict[str, Any] | None:
    """Get a song by id."""
    stmt: Select = select(songs).where(songs.c.id == song_id)
    res: Result = await conn.execute(stmt)
    row = res.mappings().first()
    return dict(row) if row else None


async def list_recent_songs(
    conn: AsyncConnection,
    limit: int = 20,
    include_drafts: bool = False,
) -> list[dict[str, Any]]:
    """List recent songs."""
    conditions = [] if include_drafts else [songs.c.is_draft.is_(False)]
    stmt = select(songs).where(and_(*conditions)).order_by(songs.c.created_at.desc()).limit(limit)
    res: Result = await conn.execute(stmt)
    return [dict(m) for m in res.mappings().all()]


async def search_songs(
    conn: AsyncConnection,
    query: str,
    limit: int = 50,
    include_drafts: bool = False,
) -> list[dict[str, Any]]:
    """Search songs with pg_trgm similarity fallback to ILIKE."""
    term = (query or '').strip()
    if not term:
        return []

    like_any = f'%{term}%'
    like_prefix = f'{term}%'
    base_conditions = [
        or_(
            songs.c.translated_title.ilike(like_any),
            songs.c.original_title.ilike(like_any),
            songs.c.artist.ilike(like_any),
            songs.c.chordpro_content.ilike(like_any),
        ),
    ]
    if not include_drafts:
        base_conditions.append(songs.c.is_draft.is_(False))

    # Check if pg_trgm is available; if not, keep simple ILIKE + priority ordering
    has_trgm = False
    try:
        res = await conn.execute(text("SELECT 1 FROM pg_extension WHERE extname = 'pg_trgm'"))
        has_trgm = res.first() is not None
    except Exception as _exc:  # noqa: BLE001
        has_trgm = False

    if not has_trgm:
        priority = case(
            (songs.c.translated_title.ilike(like_prefix), literal(1)),
            (songs.c.translated_title.ilike(like_any), literal(2)),
            (songs.c.original_title.ilike(like_any), literal(3)),
            (songs.c.artist.ilike(like_any), literal(4)),
            else_=literal(5),
        ).label('priority')
        stmt = (
            select(songs, priority)
            .where(and_(*base_conditions))
            .order_by(priority.asc(), songs.c.created_at.desc())
            .limit(limit)
        )
        res2: Result = await conn.execute(stmt)
        maps2 = res2.mappings().all()
        return [{col.name: m.get(col.name, None) for col in songs.c} for m in maps2]

    # pg_trgm-enhanced ranking
    title_sim = func.similarity(songs.c.translated_title, term)
    orig_sim = func.similarity(songs.c.original_title, term)
    artist_sim = func.similarity(songs.c.artist, term)
    lyrics_sim = func.similarity(songs.c.chordpro_content, term)
    title_prefix_bonus = case(
        (songs.c.translated_title.ilike(like_prefix), literal(0.1)),
        else_=literal(0),
    )
    score = (
        (title_sim * literal(0.5))
        + (orig_sim * literal(0.2))
        + (artist_sim * literal(0.3))
        + (lyrics_sim * literal(0.2))
        + title_prefix_bonus
    ).label('score')
    # keep implicit thresholding; datasets are small and curated

    prefix_first = case(
        (songs.c.translated_title.ilike(like_prefix), literal(0)),
        else_=literal(1),
    ).label('prefix_first')

    stmt = (
        select(songs, score)
        .where(and_(*base_conditions))
        .order_by(prefix_first.asc(), score.desc(), songs.c.created_at.desc())
        .limit(limit)
    )
    res3: Result = await conn.execute(stmt)
    maps3 = res3.mappings().all()
    return [{col.name: m.get(col.name, None) for col in songs.c} for m in maps3]
