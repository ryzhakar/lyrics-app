from __future__ import annotations

import asyncio
from logging.config import fileConfig
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from sqlalchemy.engine import Connection

from alembic import context as alembic_context
from app.db import engine as app_engine
from app.db import metadata
from app.settings import settings

config = alembic_context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = metadata


def run_migrations_offline() -> None:
    url = settings.database_url
    alembic_context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={'paramstyle': 'named'},
    )
    with alembic_context.begin_transaction():
        alembic_context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    alembic_context.configure(connection=connection, target_metadata=target_metadata)
    with alembic_context.begin_transaction():
        alembic_context.run_migrations()


async def run_migrations_online() -> None:
    connectable = app_engine
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)


if alembic_context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
