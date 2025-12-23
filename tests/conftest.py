# tests/conftest.py
import os
import shutil
import pytest

TMP_DIR = os.path.join(os.path.dirname(__file__), ".tmp_test")
TEST_DB_PATH = os.path.join(TMP_DIR, "test.db")
TEST_DB_URL = f"sqlite:///{TEST_DB_PATH}"

# CRITICAL: set DB url BEFORE app import
os.environ["DATABASE_URL"] = TEST_DB_URL

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import get_db, SessionLocal, Base, engine
from app.models.tenant import Tenant


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    os.makedirs(TMP_DIR, exist_ok=True)
    yield
    shutil.rmtree(TMP_DIR, ignore_errors=True)


@pytest.fixture(autouse=True)
def override_db():
    """
    🔥 CRITICAL FIX:
    - DB is RESET before each test
    - Guarantees test isolation
    """

    # 💣 Drop everything
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    def _get_db():
        db = SessionLocal()
        try:
            # تضمین tenant پیش‌فرض
            if not db.query(Tenant).first():
                db.add(Tenant(name="default"))
                db.commit()

            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c
