import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_register_success():
    response = client.post(
        "/auth/register",
        json={
            "email": "user1@example.com",
            "password": "strongpassword123",
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert "id" in data
    assert data["email"] == "user1@example.com"
    assert "password" not in data
    assert "hashed_password" not in data


def test_register_duplicate_email():
    payload = {
        "email": "duplicate@example.com",
        "password": "password123",
    }

    # first register
    r1 = client.post("/auth/register", json=payload)
    assert r1.status_code == 201

    # duplicate register
    r2 = client.post("/auth/register", json=payload)
    assert r2.status_code == 400

    body = r2.json()
    assert body["detail"] == "Email already registered"


def test_login_success():
    email = "login@example.com"
    password = "password123"

    # register first
    r = client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )
    assert r.status_code == 201

    # login
    response = client.post(
        "/auth/login",
        data={
            "username": email,
            "password": password,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    # refresh token must NOT exist in this stage
    assert "refresh_token" not in data


def test_login_invalid_credentials():
    response = client.post(
        "/auth/login",
        data={
            "username": "notfound@example.com",
            "password": "wrongpassword",
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 401

    body = response.json()
    assert body["detail"] == "Invalid credentials"
