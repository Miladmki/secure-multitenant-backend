# app/api/v1/tests/test_refresh_flow.py
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_refresh_flow_success_and_rotation():
    email = "flow@example.com"
    password = "pass123456"

    # register
    r = client.post("/auth/register", json={"email": email, "password": password})
    assert r.status_code == 201

    # login (get initial tokens)
    login = client.post(
        "/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login.status_code == 200
    body = login.json()
    assert "access_token" in body and "refresh_token" in body
    refresh_token = body["refresh_token"]

    # refresh (JSON)
    refresh = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh.status_code == 200
    refreshed = refresh.json()
    assert "access_token" in refreshed
    assert "refresh_token" in refreshed
    new_refresh = refreshed["refresh_token"]

    # old refresh must now be invalid (revoked)
    refresh_again = client.post("/auth/refresh", json={"refresh_token": refresh_token})
    assert refresh_again.status_code == 401
    assert refresh_again.json()["detail"] == "Invalid or expired refresh token"

    # new refresh must be valid
    refresh_new = client.post("/auth/refresh", json={"refresh_token": new_refresh})
    assert refresh_new.status_code == 200
    refreshed_2 = refresh_new.json()
    assert "access_token" in refreshed_2
    assert "refresh_token" in refreshed_2


def test_refresh_invalid_token():
    resp = client.post("/auth/refresh", json={"refresh_token": "non-existent-token"})
    assert resp.status_code == 401
    assert resp.json()["detail"] == "Invalid or expired refresh token"
