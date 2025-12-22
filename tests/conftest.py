# tests/conftest.py
import os
import shutil
import pytest
from fastapi.testclient import TestClient
from alembic import command
from alembic.config import Config
from app.main import app
from app.core.database import get_db, SessionLocal

TMP_DIR = os.path.join(os.path.dirname(__file__), ".tmp_test")
TEST_DB_PATH = os.path.join(TMP_DIR, "test.db")
TEST_DB_URL = f"sqlite:///{TEST_DB_PATH}"


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    os.makedirs(TMP_DIR, exist_ok=True)

    # override DB URL globally
    os.environ["DATABASE_URL"] = TEST_DB_URL

    # run migrations
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", TEST_DB_URL)
    command.upgrade(alembic_cfg, "head")

    yield

    shutil.rmtree(TMP_DIR, ignore_errors=True)


@pytest.fixture(autouse=True)
def override_db():
    def _get_db():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.rollback()
            db.close()

    app.dependency_overrides[get_db] = _get_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c
