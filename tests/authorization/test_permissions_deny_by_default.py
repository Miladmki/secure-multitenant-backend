# tests/authorization/test_permissions_deny_by_default.py

from fastapi.testclient import TestClient


def test_permission_not_defined_is_denied(client: TestClient):
    """
    If permission is not registered in POLICY_REGISTRY → deny.
    """

    client.post(
        "/auth/register",
        json={"email": "user@example.com", "password": "password123"},
    )

    login = client.post(
        "/auth/login",
        json={"email": "user@example.com", "password": "password123"},
    )

    token = login.json()["access_token"]

    # فرض کن این endpoint permission جدیدی دارد که policy ندارد
    r = client.get(
        "/admin/dashboard",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert r.status_code == 403
