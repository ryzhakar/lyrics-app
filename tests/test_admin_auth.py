from __future__ import annotations

import bcrypt
import pytest
from sqlalchemy import insert
import uuid

from app.auth import AdminAuth
from app.db import admin_users, engine
from app.settings import settings


class _Req:
    def __init__(self, data: dict[str, str]):
        self._data = data
        self.session: dict[str, str] = {}

    async def form(self) -> dict[str, str]:
        return self._data


@pytest.mark.asyncio
async def test_admin_login_success() -> None:  # type: ignore[no-untyped-def]
    email = f'user+{uuid.uuid4().hex[:8]}@localhost'
    pw = 'secret123!'
    pw_hash = bcrypt.hashpw(pw.encode(), bcrypt.gensalt()).decode()
    from sqlalchemy.ext.asyncio import AsyncConnection

    async with engine.begin() as conn:  # type: ignore[assignment]
        assert isinstance(conn, AsyncConnection)
        await conn.execute(
            insert(admin_users).values(email=email, password_hash=pw_hash),
        )

    req = _Req({'username': email, 'password': pw})
    auth = AdminAuth(settings.secret_key)
    ok = await auth.login(req)
    assert ok is True
    assert req.session.get('admin_email') == email


@pytest.mark.asyncio
async def test_admin_login_failure_wrong_password() -> None:  # type: ignore[no-untyped-def]
    email = f'test+{uuid.uuid4().hex[:8]}@localhost'
    pw_hash = bcrypt.hashpw('rightpass'.encode(), bcrypt.gensalt()).decode()
    from sqlalchemy.ext.asyncio import AsyncConnection

    async with engine.begin() as conn:  # type: ignore[assignment]
        assert isinstance(conn, AsyncConnection)
        await conn.execute(
            insert(admin_users).values(email=email, password_hash=pw_hash),
        )

    req = _Req({'username': email, 'password': 'wrongpass'})
    auth = AdminAuth(settings.secret_key)
    ok = await auth.login(req)
    assert ok is False
