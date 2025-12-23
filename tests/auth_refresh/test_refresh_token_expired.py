# tests/auth_refresh/test_refresh_token_expired.py

from datetime import datetime, timedelta

from app.models.refresh_token import RefreshToken


def test_refresh_token_expired(client, db_session):
    # ثبت‌نام کاربر
    r = client.post(
        "/auth/register",
        json={"email": "expired@example.com", "password": "password123"},
    )
    assert r.status_code == 201

    # لاگین
    r = client.post(
        "/auth/login",
        json={"email": "expired@example.com", "password": "password123"},
    )
    assert r.status_code == 200

    refresh_token = r.json()["refresh_token"]

    # منقضی کردن refresh token در DB
    rt = (
        db_session.query(RefreshToken)
        .filter(RefreshToken.token == refresh_token)
        .first()
    )
    assert rt is not None

    rt.expires_at = datetime.utcnow() - timedelta(minutes=1)
    db_session.commit()

    # تلاش برای refresh
    r = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert r.status_code == 401
    assert "Invalid or expired refresh token" in r.text
