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

# 🔴 CRITICAL:
# DATABASE_URL must be set BEFORE importing app or database engine
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
    """
    - Create temp directory for SQLite DB
    - Cleanup after all tests
    """
    os.makedirs(TMP_DIR, exist_ok=True)
    yield
    shutil.rmtree(TMP_DIR, ignore_errors=True)

# ------------------------------------------------------------------
# Raw DB session fixture (for direct DB manipulation in tests)
# ------------------------------------------------------------------

@pytest.fixture
def db_session():
    """
    Gives direct access to DB session
    (used in security tests like refresh token expiry / revoke)
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()

# ------------------------------------------------------------------
# Dependency override for FastAPI
# ------------------------------------------------------------------

@pytest.fixture(autouse=True)
def override_db():
    """
    🔥 CRITICAL FIX:
    - Drop & recreate ALL tables before EACH test
    - Guarantees full isolation between tests
    - Ensures default tenant always exists
    """

    # 💣 Hard reset schema
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    def _get_db():
        db = SessionLocal()
        try:
            # Ensure default tenant exists
            if not db.query(Tenant).first():
                db.add(Tenant(name="default"))
                db.commit()

            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = _get_db
    yield
    app.dependency_overrides.clear()

# ------------------------------------------------------------------
# Test client
# ------------------------------------------------------------------

@pytest.fixture
def client():
    """
    FastAPI TestClient with overridden DB dependency
    """
    with TestClient(app) as c:
        yield c
