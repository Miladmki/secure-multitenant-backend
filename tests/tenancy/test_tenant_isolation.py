import uuid
from sqlalchemy.orm import Session

from app.models.user import User
from app.models.tenant import Tenant


def unique_email(local: str = "user", domain: str = "example.com") -> str:
    suffix = uuid.uuid4().hex[:6]
    return f"{local}_{suffix}@{domain}"


def create_tenant(db: Session, prefix: str | None = None) -> Tenant:
    name = prefix or "tenant"
    tenant = Tenant(name=f"{name}_{uuid.uuid4().hex[:6]}")
    db.add(tenant)
    db.commit()
    db.refresh(tenant)
    return tenant


def create_user(db: Session, tenant: Tenant) -> User:
    user = User(
        email=unique_email(),
        hashed_password="fakehashed",
        tenant_id=tenant.id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def auth_header(tenant_id: int) -> dict[str, str]:
    return {"Authorization": f"Bearer faketoken-for-{tenant_id}"}


def test_cross_tenant_read_forbidden(client, db_session):
    tenant_a = create_tenant(db_session, "tenantA")
    tenant_b = create_tenant(db_session, "tenantB")
    create_user(db_session, tenant_b)

    response = client.get(
        "/users/",
        headers=auth_header(tenant_a.id),
    )

    assert response.status_code in (401, 403)


def test_cross_tenant_update_forbidden(client, db_session):
    tenant_a = create_tenant(db_session, "tenantA")
    tenant_b = create_tenant(db_session, "tenantB")
    user_b = create_user(db_session, tenant_b)

    response = client.put(
        f"/users/{user_b.id}",
        json={"email": "hacked@example.com"},
        headers=auth_header(tenant_a.id),
    )

    assert response.status_code in (401, 403)


def test_cross_tenant_delete_forbidden(client, db_session):
    tenant_a = create_tenant(db_session, "tenantA")
    tenant_b = create_tenant(db_session, "tenantB")
    user_b = create_user(db_session, tenant_b)

    response = client.delete(
        f"/users/{user_b.id}",
        headers=auth_header(tenant_a.id),
    )

    assert response.status_code in (401, 403)

    db_session.expire_all()
