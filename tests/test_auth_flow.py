# tests/test_auth_flow.py (جدید)
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_login_json_payload():
    email = "jsonlogin@example.com"
    password = "strongjsonpass"

    client.post("/auth/register", json={"email": email, "password": password})

    # login via JSON
    resp = client.post("/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
