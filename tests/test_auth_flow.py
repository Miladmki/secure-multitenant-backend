from fastapi.testclient import TestClient
from app.main import app
from uuid import uuid4

client = TestClient(app)


def test_login_and_get_current_user():
    unique_email = f"test_{uuid4().hex}@example.com"

    # 1) ثبت‌نام
    r = client.post(
        "/auth/register",
        json={"email": unique_email, "password": "testpassword123"},
    )
    # اگر ثبت‌نام باز هم ارور داد، با پیغام و وضعیتش ادامه بده
    assert r.status_code in (200, 201)

    # 2) لاگین و گرفتن توکن
    response = client.post(
        "/auth/login", json={"email": unique_email, "password": "testpassword123"}
    )
    assert response.status_code == 200

    access_token = response.json()["access_token"]
    assert access_token

    # 3) دسترسی به route محافظت‌شده
    response = client.get(
        "/users/me", headers={"Authorization": f"Bearer {access_token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == unique_email
