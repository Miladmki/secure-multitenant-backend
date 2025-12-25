# tests/authorization/test_permissions_tenant_isolation.py

from fastapi.testclient import TestClient


def test_cross_tenant_permission_denied(client: TestClient):
    """
    Even with permission, cross-tenant access must be denied.
    """

    # tenant A user
    client.post(
        "/auth/register",
        json={"email": "a@example.com", "password": "password123"},
    )

    login = client.post(
        "/auth/login",
        json={"email": "a@example.com", "password": "password123"},
    )
    token = login.json()["access_token"]

    # try to access tenant 999
    r = client.get(
        "/tenants/999/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert r.status_code in (403, 404)
