import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base, get_db
from app.core.config import settings
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture(autouse=True)
def setup_database():
    # دیتابیس تست جداگانه
    engine = create_engine(
        "sqlite:///./test.db", connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    # ساخت جدول‌ها
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # override dependency
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield
    Base.metadata.drop_all(bind=engine)
