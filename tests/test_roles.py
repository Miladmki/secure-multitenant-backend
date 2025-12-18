import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from collections.abc import Generator

from app.main import app
from app.core.database import get_db, Base
from app.models import tenant
from app.models.user import User
from app.models.role import Role
from app.core.security import create_access_token

client = TestClient(app)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """Fixture برای گرفتن یک session دیتابیس"""
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def override_get_db(db_session: Session):
    """استفاده از همان session در runtime و تست"""
    app.dependency_overrides[get_db] = lambda: db_session


@pytest.fixture(autouse=True)
def clean_db(db_session: Session):
    """پاک کردن دیتابیس قبل از هر تست"""
    for table in reversed(Base.metadata.sorted_tables):
        db_session.execute(table.delete())
    db_session.commit()


def create_user_with_role(db: Session, role_name: str | None):
    """کاربر تستی بساز و در صورت نیاز نقش بده"""
    email = f"{uuid.uuid4()}@example.com"  # ایمیل یکتا
    user = User(email=email, hashed_password="fakehashed", tenant_id=1)
    db.add(user)
    db.commit()
    db.refresh(user)

    if role_name:
        role = db.query(Role).filter(Role.name == role_name, Role.tenant_id == tenant.id).first()
        if not role:
            role = Role(name=role_name)
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
