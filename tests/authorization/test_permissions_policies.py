# tests/authorization/test_permissions_policies.py

from fastapi.testclient import TestClient


def test_user_cannot_update_other_user(client: TestClient):
    """
    SelfAccessPolicy should deny modifying other users.
    """

    # user 1
    client.post(
        "/auth/register",
        json={"email": "u1@example.com", "password": "password123"},
    )

    # user 2
    client.post(
        "/auth/register",
        json={"email": "u2@example.com", "password": "password123"},
    )

    login = client.post(
        "/auth/login",
        json={"email": "u1@example.com", "password": "password123"},
    )
    token = login.json()["access_token"]

    # try to update user 2
    r = client.put(
        "/users/2?email=hacked@example.com",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert r.status_code == 403
