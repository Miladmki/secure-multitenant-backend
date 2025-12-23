# tests/test_users_me.py

def test_me_authenticated(client):
    email = "meuser@example.com"
    password = "meuserpass123"

    # register
    r = client.post("/auth/register", json={"email": email, "password": password})
    assert r.status_code == 201

    # login (get tokens)
    login = client.post(
        "/auth/login",
        data={"username": email, "password": password},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert login.status_code == 200
    tokens = login.json()
    access_token = tokens["access_token"]

    # /users/me with Authorization header
    me = client.get("/users/me", headers={"Authorization": f"Bearer {access_token}"})
    assert me.status_code == 200
    body = me.json()
    assert body["email"] == email
    assert "id" in body


def test_me_unauthenticated(client):
    me = client.get("/users/me")
    assert me.status_code == 401
    assert me.json()["detail"] in (
        "Not authenticated",
        "Could not validate credentials",
    )
