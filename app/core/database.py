from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings


DATABASE_URL = settings.effective_database_url

# حذف محدودیت SQLite و اجازه دادن به PostgreSQL برای محیط تست
if settings.environment == "test":
    # در اینجا دیگر فقط چک نمی‌شود که از SQLite استفاده کنید
    # در صورتی که از PostgreSQL یا هر دیتابیس دیگری استفاده کنید، مشکلی نخواهد بود
    pass


# استفاده از URL دیتابیس برای اتصال
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
