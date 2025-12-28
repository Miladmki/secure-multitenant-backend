import os
import shutil
import pytest
from dotenv import load_dotenv
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# ------------------------------------------------------------------
# Load test environment BEFORE importing app
# ------------------------------------------------------------------

BASE_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, ".."))

load_dotenv(os.path.join(PROJECT_ROOT, ".env.test"), override=True)

assert os.getenv("ENVIRONMENT") == "test"
assert os.getenv("SECRET_KEY")
assert os.getenv("AUDIT_SIGNING_KEY")

# ------------------------------------------------------------------
# Test database path
# ------------------------------------------------------------------

TMP_DIR = os.path.join(BASE_DIR, ".tmp_test")
TEST_DB_PATH = os.path.join(TMP_DIR, "test.db")

os.makedirs(TMP_DIR, exist_ok=True)
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DB_PATH}"

# ------------------------------------------------------------------
# Imports AFTER env is fully loaded
# ------------------------------------------------------------------

from app.main import app
from app.core.database import get_db, Base, engine
from app.models.tenant import Tenant

# ------------------------------------------------------------------
# Test session factory
# ------------------------------------------------------------------

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

# ------------------------------------------------------------------
# Full lifecycle: schema + engine + filesystem
# ------------------------------------------------------------------


@pytest.fixture(scope="session", autouse=True)
def test_database_lifecycle():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
    shutil.rmtree(TMP_DIR, ignore_errors=True)


# ------------------------------------------------------------------
# Database session per test
# ------------------------------------------------------------------


@pytest.fixture
def db_session():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()


# ------------------------------------------------------------------
# Dependency override
# ------------------------------------------------------------------


@pytest.fixture(autouse=True)
def override_db(db_session):
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
