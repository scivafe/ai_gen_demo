from fastapi.testclient import TestClient


def test_signup(client: TestClient) -> None:
    resp = client.post(
        "/auth/signup", json={"username": "alice", "password": "pass123"}
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["username"] == "alice"
    assert "id" in data


def test_signup_duplicate(client: TestClient) -> None:
    client.post("/auth/signup", json={"username": "alice", "password": "pass123"})
    resp = client.post("/auth/signup", json={"username": "alice", "password": "other"})
    assert resp.status_code == 400
    assert "already taken" in resp.json()["detail"]


def test_login(client: TestClient) -> None:
    client.post("/auth/signup", json={"username": "alice", "password": "pass123"})
    resp = client.post("/auth/login", json={"username": "alice", "password": "pass123"})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_wrong_password(client: TestClient) -> None:
    client.post("/auth/signup", json={"username": "alice", "password": "pass123"})
    resp = client.post("/auth/login", json={"username": "alice", "password": "wrong"})
    assert resp.status_code == 401


def test_login_nonexistent_user(client: TestClient) -> None:
    resp = client.post("/auth/login", json={"username": "ghost", "password": "pass"})
    assert resp.status_code == 401


def test_me(client: TestClient, auth_headers: dict[str, str]) -> None:
    resp = client.get("/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["username"] == "testuser"


def test_me_no_token(client: TestClient) -> None:
    resp = client.get("/auth/me")
    assert resp.status_code == 401


def test_me_invalid_token(client: TestClient) -> None:
    resp = client.get("/auth/me", headers={"Authorization": "Bearer garbage"})
    assert resp.status_code == 401
