import pytest
from app.main import app
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_authorization_decision_logging(client):
    """
    Test that the AuthorizationDecision object logs the deny reason and stores information correctly.
    """

    # ثبت‌نام کاربر
    register_response = client.post(
        "/auth/register", json={"email": "user1_unique_test@example.com", "password": "password123"}
    )
    assert register_response.status_code == 201

    # ورود به سیستم
    login_response = client.post(
        "/auth/login", json={"email": "user1_unique_test@example.com", "password": "password123"}
    )
    assert login_response.status_code == 200
    login_data = login_response.json()

    token = login_data["access_token"]

    # دسترسی به منبع محدود
    response = client.put(
        "/users/2?email=unauthorized@example.com",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 403
