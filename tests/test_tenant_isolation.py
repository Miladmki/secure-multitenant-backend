import pytest
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.user import User, Tenant

# -------------------------
# Helper برای ساخت داده تست
# -------------------------


def create_tenant(db: Session, name: str) -> Tenant:
    tenant = Tenant(name=name)
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant


def create_user(db: Session, email: str, tenant: Tenant) -> User:
    user = User(email=email, hashed_password="fakehashed", tenant_id=tenant.id)
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
