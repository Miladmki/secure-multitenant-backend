# tests/test_auth_flow.py

def test_login_json_payload(client):
    email = "jsonlogin@example.com"
    password = "strongjsonpass"

    client.post("/auth/register", json={"email": email, "password": password})

    # login via JSON
    resp = client.post("/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
