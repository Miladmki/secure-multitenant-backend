# app/api/v1/tests/test_auth_basic.py


def test_register_success(client):
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


def test_register_duplicate_email(client):
    payload = {
        "email": "duplicate@example.com",
        "password": "password123",
    }
    r1 = client.post("/auth/register", json=payload)
    assert r1.status_code == 201

    r2 = client.post("/auth/register", json=payload)
    assert r2.status_code == 400
    body = r2.json()
    assert body["detail"] == "Email already registered"


def test_login_success_oauth2_form(client):
    email = "login_form@example.com"
    password = "password123"

    # register
    r = client.post("/auth/register", json={"email": email, "password": password})
    assert r.status_code == 201

    # login via OAuth2 form
    response = client.post(
        "/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_success_json_body(client):
    email = "login_json@example.com"
    password = "password123"

    # register
    r = client.post("/auth/register", json={"email": email, "password": password})
    assert r.status_code == 201

    # login via JSON body
    response = client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client):
    response = client.post(
        "/auth/login",
        data={"username": "notfound@example.com", "password": "wrongpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 401
    body = response.json()
    assert body["detail"] == "Invalid credentials"
