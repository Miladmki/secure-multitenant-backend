import pytest
import uuid
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from collections.abc import Generator

from app.main import app
from app.core.database import get_db, Base
from app.core.security import create_access_token
from app.models.user import User
from app.models.role import Role
from app.models.tenant import Tenant

client = TestClient(app)


@pytest.fixture
def db_session() -> Generator[Session, None, None]:
    """یک session دیتابیس برای تست‌ها فراهم می‌کند"""
    db = next(get_db())
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def override_get_db(db_session: Session):
    """اطمینان از اینکه dependency get_db در runtime از همان session تست استفاده کند"""
    app.dependency_overrides[get_db] = lambda: db_session


@pytest.fixture(autouse=True)
def clean_db(db_session: Session):
    """پاک کردن تمام جداول قبل از هر تست تا حالت ایزوله تضمین شود"""
    for table in reversed(Base.metadata.sorted_tables):
        db_session.execute(table.delete())
    db_session.commit()


def create_tenant(db: Session, name: str | None = None) -> Tenant:
    """ایجاد یک tenant جدید و بازگرداندن آن"""
    tenant = Tenant(name=name or f"tenant-{uuid.uuid4()}")
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant


def create_user_with_roles(db: Session, tenant: Tenant, roles: list[str] | None = None):
    """
    کاربر می‌سازد، نقش‌ها را به او اختصاص می‌دهد و توکن JWT برمی‌گرداند.
    - roles: لیست نام نقش‌ها (مثلاً ["admin", "user"])
    """
    email = f"{uuid.uuid4()}@example.com"
    user = User(email=email, hashed_password="fakehashed", tenant_id=tenant.id)
    db.add(user)
    db.commit()
    db.refresh(user)

    if roles:
        for rname in roles:
            role = db.query(Role).filter(Role.name == rname).first()
            if not role:
                role = Role(name=rname)
                db.add(role)
                db.commit()
                db.refresh(role)
            # فرض: رابطه many-to-many user.roles موجود است
            user.roles.append(role)
        db.commit()
        db.refresh(user)

    token = create_access_token(subject=str(user.id))
    return token, user


# -------------------------
# تست‌های ترکیبی role + tenant
# -------------------------


def test_admin_access_same_tenant(db_session: Session):
    """
    کاربر admin در tenant درست باید بتواند به داشبورد tenant دسترسی داشته باشد (200).
    """
    t = create_tenant(db_session, "tenant-A")
    token, user = create_user_with_roles(db_session, t, roles=["admin"])

    resp = client.get(f"/tenants/{t.id}/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200


def test_admin_access_other_tenant_forbidden(db_session: Session):
    """
    کاربر admin در tenant B نباید به داشبورد tenant A دسترسی داشته باشد (403).
    """
    tA = create_tenant(db_session, "tenant-A")
    tB = create_tenant(db_session, "tenant-B")

    token_b, user_b = create_user_with_roles(db_session, tB, roles=["admin"])

    resp = client.get(f"/tenants/{tA.id}/dashboard", headers={"Authorization": f"Bearer {token_b}"})
    assert resp.status_code == 403


def test_user_role_forbidden(db_session: Session):
    """
    کاربر با نقش user در tenant خودش نباید به داشبورد tenant دسترسی admin‌گونه داشته باشد (403).
    """
    t = create_tenant(db_session, "tenant-C")
    token, user = create_user_with_roles(db_session, t, roles=["user"])

    resp = client.get(f"/tenants/{t.id}/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403


def test_multi_role_user_has_admin_access(db_session: Session):
    """
    کاربر با نقش‌های user و admin باید دسترسی admin را داشته باشد (ترکیب نقش‌ها).
    """
    t = create_tenant(db_session, "tenant-D")
    token, user = create_user_with_roles(db_session, t, roles=["user", "admin"])

    resp = client.get(f"/tenants/{t.id}/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200


def test_user_without_role_forbidden(db_session: Session):
    """
    کاربر بدون هیچ نقش مشخصی نباید به داشبورد tenant دسترسی داشته باشد (403).
    """
    t = create_tenant(db_session, "tenant-E")
    token, user = create_user_with_roles(db_session, t, roles=None)

    resp = client.get(f"/tenants/{t.id}/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 403


def test_admin_global_endpoint_requires_admin_role(db_session: Session):
    """
    endpoint سراسری admin (مثلاً /admin/dashboard) فقط برای نقش admin قابل دسترسی است.
    """
    t = create_tenant(db_session, "tenant-global")
    token_admin, _ = create_user_with_roles(db_session, t, roles=["admin"])
    token_user, _ = create_user_with_roles(db_session, t, roles=["user"])

    resp_ok = client.get("/admin/dashboard", headers={"Authorization": f"Bearer {token_admin}"})
    assert resp_ok.status_code == 200

    resp_forbidden = client.get("/admin/dashboard", headers={"Authorization": f"Bearer {token_user}"})
    assert resp_forbidden.status_code == 403
