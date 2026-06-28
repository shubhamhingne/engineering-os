"""Alembic environment — schema migrations for production (BR-04).

Tests still build the schema with `Base.metadata.create_all` (fast, throwaway in-memory DBs); Alembic
is the *production* path so the schema can evolve without data loss. Both read the same
`Base.metadata`, so they cannot drift."""
from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from engineering_os.adapters.db import models  # noqa: F401  (register tables on Base)
from engineering_os.config import settings
from engineering_os.db import Base

config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata, render_as_batch=True
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
