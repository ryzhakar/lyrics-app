from __future__ import annotations

from typing import TYPE_CHECKING, Any

from sqlalchemy import insert, select, update

if TYPE_CHECKING:  # pragma: no cover
    from sqlalchemy.engine import Result
    from sqlalchemy.ext.asyncio import AsyncConnection

from app.db import admin_users


async def create_admin(conn: AsyncConnection, email: str, password_hash: str) -> dict[str, Any]:
    """Create an admin user."""
    stmt = (
        insert(admin_users).values(email=email, password_hash=password_hash).returning(admin_users)
    )
    res: Result = await conn.execute(stmt)
    return dict(res.mappings().one())


async def get_admin_by_email(conn: AsyncConnection, email: str) -> dict[str, Any] | None:
    """Get an admin by email."""
    stmt = select(admin_users).where(admin_users.c.email == email)
    res: Result = await conn.execute(stmt)
    row = res.mappings().first()
    return dict(row) if row else None


async def update_admin_password(conn: AsyncConnection, email: str, password_hash: str) -> None:
    """Update admin password hash by email."""
    stmt = (
        update(admin_users).where(admin_users.c.email == email).values(password_hash=password_hash)
    )
    await conn.execute(stmt)
