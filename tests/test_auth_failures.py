# tests/test_auth_failures.py
from jose import jwt
from app.core.config import settings


def test_me_without_token(client):
    """
    1️⃣ درخواست به route محافظت‌شده بدون ارسال توکن
    انتظار: 401 Unauthorized
    """
    response = client.get("/users/me")
    assert response.status_code == 401


def test_me_with_invalid_token(client):
    """
    2️⃣ ارسال توکن خراب / نامعتبر
    انتظار: 401 Unauthorized
    """
    response = client.get(
        "/users/me",
        headers={"Authorization": "Bearer invalid.token.value"},
    )
    assert response.status_code == 401


def test_me_user_not_found(client):
    """
    3️⃣ توکن معتبر ولی user مربوط به sub وجود ندارد
    (مثلاً user_id = 999)
    انتظار معماری ما: 401 Unauthorized
    """

    token = jwt.encode(
        {"sub": "999"},
        settings.secret_key,
        algorithm=settings.algorithm,
    )

    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
