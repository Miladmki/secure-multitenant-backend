from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_refresh_token_success():
    """
    سناریو:
    - ثبت‌نام
    - لاگین
    - دریافت refresh token
    - درخواست refresh
    - دریافت access token جدید
    """

    email = f"test_{uuid4().hex}@example.com"
    password = "testpassword123"

    # 1) register
    r = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )
    assert r.status_code == 201

    # 2) login
    r = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": "testpassword123",
        },
    )

    assert r.status_code == 200

    body = r.json()
    assert "access_token" in body
    assert "refresh_token" in body

    refresh_token = body["refresh_token"]
    old_access_token = body["access_token"]

    # 3) refresh
    r = client.post(
        "/auth/refresh",
        json={
            "refresh_token": refresh_token,
        },
    )

    # فعلاً fail می‌شود (501)
    assert r.status_code == 200

    refreshed = r.json()

    assert "access_token" in refreshed
    assert refreshed["access_token"] != old_access_token
    assert refreshed["token_type"] == "bearer"
