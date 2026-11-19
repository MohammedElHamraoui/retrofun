from logging.config import fileConfig
from typing import Any

from alembic import context
from sqlalchemy import engine_from_config, pool

from retrofun import models  # noqa: F401
from retrofun.config import settings
from retrofun.db import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata
config.set_main_option("sqlalchemy.url", settings.sqlalchemy_url)


def include_object(
    object: Any, name: str | None, type_: str, reflected: bool, compare_to: Any
) -> bool:
    """
    Filter objects during autogenerate.
    - Ignore foreign_key_constraint diffs (schema-qualification noise).
    - Ignore the alembic_version table (PostgreSQL reflection schema mismatch noise).
    """
    return not (
        type_ == "foreign_key_constraint" or (type_ == "table" and name == "alembic_version")
    )


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        version_table_schema=settings.version_table_schema,
        include_object=include_object,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
            version_table_schema=settings.version_table_schema,
            include_object=include_object,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
