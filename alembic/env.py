from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

from app.core.database import Base
from app.core.database import Base
from app.models import user, refresh_token

target_metadata = Base.metadata

# -------------------------------------------------
# Alembic Config
# -------------------------------------------------
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# -------------------------------------------------
# Import Base (تنها Base پروژه)
# -------------------------------------------------
from app.core.database import Base

# -------------------------------------------------
# Import ALL models explicitly (خیلی مهم)
# -------------------------------------------------
import app.models.user
import app.models.refresh_token

# -------------------------------------------------
# Target metadata for autogenerate
# -------------------------------------------------
target_metadata = Base.metadata


# -------------------------------------------------
# Offline migrations
# -------------------------------------------------
def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


# -------------------------------------------------
# Online migrations
# -------------------------------------------------
def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


# -------------------------------------------------
# Entrypoint
# -------------------------------------------------
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
