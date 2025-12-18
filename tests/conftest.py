# tests/conftest.py
import os
import pytest
from importlib import import_module
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from fastapi import FastAPI

from app.core.database import Base, get_db

# robust import of FastAPI instance from app.main
try:
    main_mod = import_module("app.main")
    app = getattr(main_mod, "app", None)
except Exception as e:
    app = None
    import_err = e

if app is None or not isinstance(app, FastAPI):
    raise RuntimeError(
        "Could not import FastAPI instance from app.main. "
        "Ensure app/main.py defines `app = FastAPI()` and there is no file named "
        "`app.py` shadowing the package, and no circular imports. "
        f"Import error: {locals().get('import_err')}"
    )

# import models so metadata is registered WITHOUT overwriting `app` name
import_module("app.models.user")
import_module("app.models.tenant")
import_module("app.models.refresh_token")

# import tenant model for default tenant creation
import app.models.tenant as tenant_model

TEST_DB_URL = "sqlite:///./test.db"


@pytest.fixture(scope="session")
def engine():
    if os.path.exists("test.db"):
        os.remove("test.db")
    return create_engine(TEST_DB_URL, connect_args={"check_same_thread": False})


@pytest.fixture(scope="session")
def TestingSessionLocal(engine):
    return sessionmaker(bind=engine, autocommit=False, autoflush=False)


@pytest.fixture(autouse=True)
def setup_database(engine, TestingSessionLocal):
    # create fresh schema
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        # 👇 tenant پیش‌فرض بساز اگر وجود ندارد
        tenant = db.query(tenant_model.Tenant).first()
        if not tenant:
            tenant = tenant_model.Tenant(name="default")
            db.add(tenant)
            db.commit()
            db.refresh(tenant)
        try:
            yield db
        finally:
            db.close()

    # now override dependency on the FastAPI instance
    app.dependency_overrides[get_db] = override_get_db

    yield

    # teardown
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)
