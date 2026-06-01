from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context
from db.database import Base
from db.models import anime, books  # noqa: F401 - Ensure models are imported for Alembic autogenerate support
from utils.config import settings

# Alembic Config object
config = context.config

# Configure logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata for autogenerate support
target_metadata = Base.metadata


def get_database_url() -> str:
    """
    Returns the database URL from application settings.
    """
    return settings.sqlalchemy_database_uri


def run_migrations_offline() -> None:
    """
    Run migrations in offline mode.
    """

    url = get_database_url()

    # Inject URL into alembic config
    config.set_main_option("sqlalchemy.url", url)

    print(f"Using database URL (offline): {url}")

    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """
    Run migrations in online mode.
    """

    url = get_database_url()

    # Inject URL into alembic config
    config.set_main_option("sqlalchemy.url", url)

    print(f"Using database URL (online): {url}")

    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
        future=True,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
