from __future__ import annotations

import os

import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.asyncio import create_async_engine

from app import db as db_mod
from app.main import app
from app.settings import settings

# If a dedicated test DB URL is provided, switch the app engine to use it
_test_db_url = os.getenv('DATABASE_URL_TEST')
if _test_db_url:
    settings.database_url = _test_db_url  # type: ignore[assignment]
    db_mod.engine = db_mod.create_engine()  # type: ignore[attr-defined]


@pytest_asyncio.fixture(scope='session', autouse=True)
async def _prepare_test_db():
    async with db_mod.engine.begin() as conn:  # type: ignore[attr-defined]
        await conn.run_sync(db_mod.metadata.create_all)  # type: ignore[attr-defined]
    yield
    async with db_mod.engine.begin() as conn:  # type: ignore[attr-defined]
        await conn.run_sync(db_mod.metadata.drop_all)  # type: ignore[attr-defined]


@pytest_asyncio.fixture(autouse=True, scope='function')
async def _reset_engine_pool():
    await db_mod.engine.dispose()  # type: ignore[attr-defined]


@pytest_asyncio.fixture(scope='function')
async def db_conn():
    async with db_mod.engine.connect() as conn:  # type: ignore[attr-defined]
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
