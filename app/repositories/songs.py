from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import and_, case, insert, literal, or_, select

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
    """Search songs by ILIKE."""
    q = f'%{query}%'
    qp = f'{query}%'
    conditions = [
        or_(
            songs.c.translated_title.ilike(q),
            songs.c.artist.ilike(q),
            songs.c.chordpro_content.ilike(q),
        ),
    ]
    if not include_drafts:
        conditions.append(songs.c.is_draft.is_(False))
    priority = case(
        (
            songs.c.translated_title.ilike(qp),
            literal(1),
        ),
        (
            songs.c.translated_title.ilike(q),
            literal(2),
        ),
        (
            songs.c.artist.ilike(q),
            literal(3),
        ),
        else_=literal(4),
    ).label('priority')
    stmt = (
        select(songs, priority)
        .where(and_(*conditions))
        .order_by(priority.asc(), songs.c.created_at.desc())
        .limit(limit)
    )
    res: Result = await conn.execute(stmt)
    return [{k: v for k, v in dict(m).items() if k in songs.c} for m in res.mappings().all()]
