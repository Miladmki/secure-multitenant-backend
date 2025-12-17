# tests/conftest.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.core.database import Base, get_db
from app.main import app


@pytest.fixture(autouse=True)
def setup_database():
    """
    هر بار قبل از تست‌ها دیتابیس تست ساخته می‌شود و بعد از تست‌ها پاک می‌شود.
    """
    engine = create_engine(
        "sqlite:///./test.db", connect_args={"check_same_thread": False}
    )
    TestingSessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)

    # پاک‌سازی و ساخت جدول‌ها
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # override dependency برای استفاده از دیتابیس تست
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    yield

    # بعد از تست‌ها جدول‌ها پاک می‌شوند
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """
    Fixture برای FastAPI TestClient.
    همه‌ی تست‌ها می‌توانند این را به عنوان پارامتر بگیرند.
    """
    return TestClient(app)
