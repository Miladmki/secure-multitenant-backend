# tests/conftest.py

import os
import shutil
import pytest

# ------------------------------------------------------------------
# Test database configuration
# ------------------------------------------------------------------

BASE_DIR = os.path.dirname(__file__)
TMP_DIR = os.path.join(BASE_DIR, ".tmp_test")
TEST_DB_PATH = os.path.join(TMP_DIR, "test.db")
TEST_DB_URL = f"sqlite:///{TEST_DB_PATH}"

# CRITICAL: must be set before importing app/db
os.environ["DATABASE_URL"] = TEST_DB_URL

# ------------------------------------------------------------------
# Imports AFTER DATABASE_URL is set
# ------------------------------------------------------------------

from fastapi.testclient import TestClient

from app.main import app
from app.core.database import get_db, SessionLocal, Base, engine
from app.models.tenant import Tenant

# ------------------------------------------------------------------
# Session-level DB setup / teardown
# ------------------------------------------------------------------


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    os.makedirs(TMP_DIR, exist_ok=True)
    yield
    shutil.rmtree(TMP_DIR, ignore_errors=True)


# ------------------------------------------------------------------
# Raw DB session fixture
# ------------------------------------------------------------------


@pytest.fixture
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()


# ------------------------------------------------------------------
# Dependency override (CRITICAL)
# ------------------------------------------------------------------


@pytest.fixture(autouse=True)
def override_db(db_session):
    """
    - Drop & recreate schema per test
    - Ensure FastAPI and tests share the SAME session
    """

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    # ensure default tenant
    if not db_session.query(Tenant).first():
        db_session.add(Tenant(name="default"))
        db_session.commit()

    def _get_db():
        yield db_session

    app.dependency_overrides[get_db] = _get_db
    yield
    app.dependency_overrides.clear()


# ------------------------------------------------------------------
# Test client
# ------------------------------------------------------------------


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c
