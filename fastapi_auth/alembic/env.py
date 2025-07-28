from logging.config import fileConfig
from alembic import context
from fastapi_users_db_sqlalchemy.generics import GUID
import asyncio
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.database import async_db, Base
from app.auth.models import User
from app.group.models import Group, UserGroup

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,
        include_schemas=True
    )

    with context.begin_transaction():
        context.run_migrations()

async def run_migrations_online():
    async with async_db.engine.begin() as connection:
        await connection.run_sync(do_run_migrations)

if context.is_offline_mode():
    print("Cannot run migrations in offline mode with async setup")
    sys.exit(1)
else:
    asyncio.run(run_migrations_online())