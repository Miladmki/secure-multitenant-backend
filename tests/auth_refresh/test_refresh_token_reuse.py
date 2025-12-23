# tests/auth_refresh/test_refresh_token_reuse.py


def test_refresh_token_cannot_be_reused(client):
    # ثبت‌نام
    r = client.post(
        "/auth/register",
        json={"email": "reuse@example.com", "password": "password123"},
    )
    assert r.status_code == 201

    # لاگین
    r = client.post(
        "/auth/login",
        json={"email": "reuse@example.com", "password": "password123"},
    )
    assert r.status_code == 200

    refresh_token = r.json()["refresh_token"]

    # اولین refresh (باید موفق باشد)
    r1 = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert r1.status_code == 200

    # استفاده مجدد از refresh token قدیمی
    r2 = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert r2.status_code == 401
