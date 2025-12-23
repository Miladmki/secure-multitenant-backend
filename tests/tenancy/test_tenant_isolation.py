import pytest
import uuid
from sqlalchemy.orm import Session
from app.core.database import get_db, Base, engine

from app.models.user import User
from app.models.tenant import Tenant

# -------------------------
# ایزوله کردن دیتابیس بین تست‌ها
# -------------------------


@pytest.fixture(autouse=True)
def reset_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = next(get_db())
    db.add(Tenant(name="default"))
    db.commit()
    db.close()

    yield

    Base.metadata.drop_all(bind=engine)


# -------------------------
# Helper ها برای داده تست
# -------------------------


def unique_email(base_local: str = "user", domain: str = "example.com") -> str:
    suffix = uuid.uuid4().hex[:6]
    return f"{base_local}_{suffix}@{domain}"


def create_tenant(db: Session, name: str = None) -> Tenant:
    if name is None:
        # تولید نام یکتا برای جلوگیری از خطای UNIQUE
        name = f"tenant_{uuid.uuid4().hex[:6]}"
    else:
        # اگر اسم ثابت داده شد، suffix تصادفی اضافه کن تا همیشه یکتا باشد
        name = f"{name}_{uuid.uuid4().hex[:6]}"
    tenant = Tenant(name=name)
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant


def create_user(db: Session, email: str, tenant: Tenant) -> User:
    # حتی اگر ایمیل ثابت پاس داده شود، آن را یکتا می‌کنیم
    local, domain = email.split("@")
    email_unique = unique_email(local, domain)
    user = User(email=email_unique, hashed_password="fakehashed", tenant_id=tenant.id)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


# -------------------------
# تست‌های Cross-Tenant
# -------------------------


def test_cross_tenant_read_forbidden(client):
    """
    کاربر tenant A نباید بتواند کاربران tenant B را بخواند.
    """
    db = next(get_db())
    tenant_a = create_tenant(db, "tenantA")
    tenant_b = create_tenant(db, "tenantB")
    user_b = create_user(db, "userb@example.com", tenant_b)

    # شبیه‌سازی درخواست با tenant A
    response = client.get(
        "/users/", headers={"Authorization": f"Bearer faketoken-for-{tenant_a.id}"}
    )
    assert response.status_code in (401, 403)


def test_cross_tenant_update_forbidden(client):
    """
    کاربر tenant A نباید بتواند کاربر tenant B را آپدیت کند.
    """
    db = next(get_db())
    tenant_a = create_tenant(db, "tenantA")
    tenant_b = create_tenant(db, "tenantB")
    user_b = create_user(db, "userb@example.com", tenant_b)

    response = client.put(
        f"/users/{user_b.id}",
        json={"email": "hacked@example.com"},
        headers={"Authorization": f"Bearer faketoken-for-{tenant_a.id}"},
    )
    assert response.status_code in (401, 403)


def test_cross_tenant_delete_forbidden(client):
    """
    کاربر tenant A نباید بتواند کاربر tenant B را حذف کند.
    """
    db = next(get_db())
    tenant_a = create_tenant(db, "tenantA")
    tenant_b = create_tenant(db, "tenantB")
    user_b = create_user(db, "userb@example.com", tenant_b)

    response = client.delete(
        f"/users/{user_b.id}",
        headers={"Authorization": f"Bearer faketoken-for-{tenant_a.id}"},
    )
    assert response.status_code in (401, 403)
