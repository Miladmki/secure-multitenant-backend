# tests/auth_refresh/test_refresh_token_revoked.py

from app.models.refresh_token import RefreshToken


def test_revoked_refresh_token_is_invalid(client, db_session):
    # ثبت‌نام
    r = client.post(
        "/auth/register",
        json={"email": "revoked@example.com", "password": "password123"},
    )
    assert r.status_code == 201

    # لاگین
    r = client.post(
        "/auth/login",
        json={"email": "revoked@example.com", "password": "password123"},
    )
    assert r.status_code == 200

    refresh_token = r.json()["refresh_token"]

    # revoke کردن refresh token
    rt = (
        db_session.query(RefreshToken)
        .filter(RefreshToken.token == refresh_token)
        .first()
    )
    assert rt is not None

    rt.revoked = True
    db_session.commit()

    # تلاش برای refresh
    r = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert r.status_code == 401
    assert "Invalid or expired refresh token" in r.text
