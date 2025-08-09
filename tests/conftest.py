from __future__ import annotations

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text

from app.db import engine
from app.main import app


@pytest_asyncio.fixture(autouse=True, scope='function')
async def _reset_engine_pool():
    await engine.dispose()


@pytest_asyncio.fixture(scope='function')
async def db_conn():
    async with engine.connect() as conn:
        await conn.execute(text('DELETE FROM songs'))
        await conn.execute(text('DELETE FROM admin_users'))
        yield conn
        await conn.execute(text('DELETE FROM songs'))
        await conn.execute(text('DELETE FROM admin_users'))


@pytest_asyncio.fixture(scope='function')
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url='http://test') as ac:
        yield ac
