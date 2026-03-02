def test_signup_success(client):
    resp = client.post("/api/auth/signup", json={
        "name": "Alice", "email": "alice@example.com", "password": "pass1234"
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "alice@example.com"
    assert "password" not in data


def test_signup_duplicate_email(client):
    client.post("/api/auth/signup", json={
        "name": "Alice", "email": "alice@example.com", "password": "pass1234"
    })
    resp = client.post("/api/auth/signup", json={
        "name": "Alice2", "email": "alice@example.com", "password": "pass5678"
    })
    assert resp.status_code == 409


def test_login_success(client):
    client.post("/api/auth/signup", json={
        "name": "Alice", "email": "alice@example.com", "password": "pass1234"
    })
    resp = client.post("/api/auth/login", json={
        "email": "alice@example.com", "password": "pass1234"
    })
    assert resp.status_code == 200
    assert "access_token" in resp.json()


def test_login_wrong_password(client):
    client.post("/api/auth/signup", json={
        "name": "Alice", "email": "alice@example.com", "password": "pass1234"
    })
    resp = client.post("/api/auth/login", json={
        "email": "alice@example.com", "password": "wrong"
    })
    assert resp.status_code == 401


def test_me_authenticated(client, auth_headers):
    resp = client.get("/api/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "test@example.com"


def test_me_unauthenticated(client):
    resp = client.get("/api/auth/me")
    assert resp.status_code == 401
