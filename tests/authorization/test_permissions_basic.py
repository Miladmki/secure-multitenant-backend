# tests/authorization/test_permissions_basic.py

from fastapi.testclient import TestClient
from app.core.permissions import Permission


def test_admin_can_read_users(client: TestClient):
    """
    Admin role has USERS_READ permissions.
    """
    # register
    client.post(
        "/auth/register",
        json={"email": "admin@example.com", "password": "password123"},
    )

    # login
    login = client.post(
        "/auth/login",
        json={"email": "admin@example.com", "password": "password123"},
    )
    token = login.json()["access_token"]

    # access users list
    r = client.get(
        "/users/",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert r.status_code == 200
