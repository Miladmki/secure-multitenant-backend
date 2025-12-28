from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings


DATABASE_URL = settings.effective_database_url


if settings.environment == "test":
    if DATABASE_URL.startswith("sqlite:///"):
        db_path = Path(DATABASE_URL.replace("sqlite:///", "")).resolve()
        if "tests" not in db_path.parts:
            raise RuntimeError(
                "TEST environment is NOT using test database! "
                f"Current DATABASE_URL={DATABASE_URL}"
            )
    else:
        raise RuntimeError(
            "TEST environment must use SQLite test database! "
            f"Current DATABASE_URL={DATABASE_URL}"
        )


engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    future=True,
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
