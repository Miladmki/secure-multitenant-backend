# alembic/env.py
import os
from logging.config import fileConfig
from dotenv import load_dotenv

# ------------------------------------------------------------------
# Load environment variables EARLY and FORCE override
# ------------------------------------------------------------------

ENV = os.getenv("ENVIRONMENT", "dev")
env_file = f".env.{ENV}"

if not os.path.exists(env_file):
    raise RuntimeError(f"Expected env file not found: {env_file}")

load_dotenv(env_file, override=True)

print("ALEMBIC ENVIRONMENT =", ENV)
print("ALEMBIC DATABASE_URL =", os.getenv("DATABASE_URL"))

# ------------------------------------------------------------------
# Alembic imports (AFTER env is loaded)
# ------------------------------------------------------------------

from sqlalchemy import engine_from_config, pool
from alembic import context

from app.core.config import settings
from app.core.database import Base

# ------------------------------------------------------------------
# Alembic config
# ------------------------------------------------------------------

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# ------------------------------------------------------------------
# Online migration runner
# ------------------------------------------------------------------


def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.
    """

    # SINGLE source of truth: settings
    config.set_main_option(
        "sqlalchemy.url",
        settings.effective_database_url,
    )

    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
