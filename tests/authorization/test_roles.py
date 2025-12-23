import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from collections.abc import Generator

from app.main import app
from app.core.database import get_db, Base
from app.models.tenant import Tenant
from app.models.user import User
from app.models.role import Role
from app.core.security import create_access_token

client = TestClient(app)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """Fixture for getting a database session"""
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def override_get_db(db_session: Session):
    """Use same session in runtime and test"""
    app.dependency_overrides[get_db] = lambda: db_session


@pytest.fixture(autouse=True)
def clean_db(db_session: Session):
    """Clean database before each test"""
    # Clean in reverse order of foreign key dependencies
    for table in reversed(Base.metadata.sorted_tables):
        db_session.execute(table.delete())
    db_session.commit()

    # Create default tenant for tests
    tenant = Tenant(name="default")
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)


def create_user_with_role(db: Session, role_name: str | None):
    """Create test user and assign role if needed"""
    # Get default tenant
    tenant = db.query(Tenant).filter(Tenant.name == "default").first()
    if not tenant:
        tenant = Tenant(name="default")
        db.add(tenant)
        db.commit()
        db.refresh(tenant)

    email = f"{uuid.uuid4()}@example.com"
    user = User(email=email, hashed_password="fakehashed", tenant_id=tenant.id)
    db.add(user)
    db.commit()
    db.refresh(user)

    if role_name:
        role = (
            db.query(Role)
            .filter(Role.name == role_name, Role.tenant_id == tenant.id)
            .first()
        )
        if not role:
            role = Role(name=role_name, tenant_id=tenant.id)
            db.add(role)
            db.commit()
            db.refresh(role)
        user.roles.append(role)
        db.commit()
        db.refresh(user)

    token = create_access_token(subject=str(user.id))
    return token, user


def test_user_without_role(db_session: Session):
    token, user = create_user_with_role(db_session, None)
    response = client.get(
        "/admin/dashboard", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403


def test_user_with_admin_role(db_session: Session):
    token, user = create_user_with_role(db_session, "admin")
    response = client.get(
        "/admin/dashboard", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert "Welcome admin" in response.json()["msg"]


def test_user_with_user_role(db_session: Session):
    token, user = create_user_with_role(db_session, "user")
    response = client.get(
        "/admin/dashboard", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
