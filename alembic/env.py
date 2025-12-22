# ===== alembic/env.py =====
from sqlalchemy import engine_from_config, pool
from alembic import context

# Import Base
from app.core.database import Base

# 🔥 IMPORT ALL MODELS HERE (and ONLY here)
from app.models.tenant import Tenant
from app.models.user import User
from app.models.role import Role
from app.models.user_roles import user_roles
from app.models.refresh_token import RefreshToken
from app.models.item import Item

target_metadata = Base.metadata


def run_migrations_offline():
    url = (
        context.get_x_argument(as_dictionary=True).get("url")
        or context.get_ini_section("alembic")["sqlalchemy.url"]
    )
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    config = context.config

    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
