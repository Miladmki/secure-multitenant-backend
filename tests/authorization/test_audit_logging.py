from sqlalchemy import text

from app.models.audit_log import AuthorizationAuditLog
from app.core.permissions import Permission


def login_and_get_token(client, email, password):
    client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )

    response = client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    return response.json()["access_token"]


def test_permission_denied_is_logged(client, db_session):
    token = login_and_get_token(
        client,
        email="user1@test.com",
        password="password123",
    )

    response = client.get(
        "/admin/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403

    logs = db_session.query(AuthorizationAuditLog).all()
    assert len(logs) == 1

    log = logs[0]
    assert log.permission == Permission.ADMIN_DASHBOARD.value
    assert log.allowed is False
    assert log.endpoint == "/admin/dashboard"
    assert log.method == "GET"


def test_permission_allowed_is_logged(client, db_session):
    # register admin user
    client.post(
        "/auth/register",
        json={
            "email": "admin@test.com",
            "password": "password123",
        },
    )

    # get user id
    user_id = db_session.execute(
        text("SELECT id FROM users WHERE email = :email"),
        {"email": "admin@test.com"},
    ).scalar_one()

    # get tenant id (default tenant is guaranteed by conftest)
    tenant_id = db_session.execute(text("SELECT id FROM tenants LIMIT 1")).scalar_one()

    # create admin role with tenant_id
    db_session.execute(
        text(
            """
            INSERT INTO roles (name, tenant_id)
            VALUES (:name, :tenant_id)
            """
        ),
        {
            "name": "admin",
            "tenant_id": tenant_id,
        },
    )

    # attach role to user
    db_session.execute(
        text(
            """
            INSERT INTO user_roles (user_id, role_id)
            SELECT :user_id, id FROM roles WHERE name = :name
            """
        ),
        {
            "user_id": user_id,
            "name": "admin",
        },
    )

    db_session.commit()

    # login
    response = client.post(
        "/auth/login",
        json={
            "email": "admin@test.com",
            "password": "password123",
        },
    )

    token = response.json()["access_token"]

    response = client.get(
        "/admin/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    logs = db_session.query(AuthorizationAuditLog).all()
    assert len(logs) == 1

    log = logs[0]
    assert log.permission == Permission.ADMIN_DASHBOARD.value
    assert log.allowed is True
    assert log.reason == "permission granted"


def test_audit_failure_does_not_break_authorization(
    client,
    db_session,
    monkeypatch,
):
    from app.services import audit_service

    def broken_logger(*args, **kwargs):
        raise RuntimeError("audit db down")

    monkeypatch.setattr(
        audit_service,
        "log_authorization_decision",
        broken_logger,
    )

    token = login_and_get_token(
        client,
        email="admin2@test.com",
        password="password123",
    )

    response = client.get(
        "/admin/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code in (200, 403)
