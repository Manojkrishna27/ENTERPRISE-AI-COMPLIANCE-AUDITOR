def test_login_invalid(client):
    response = client.post(
        "/api/auth/login", json={"email": "invalid@test.com", "password": "wrong"}
    )
    assert response.status_code == 401


def test_login_success(client):
    response = client.post(
        "/api/auth/login", json={"email": "test@example.com", "password": "password123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["user"]["email"] == "test@example.com"


def test_protected_route_missing_token(client):
    response = client.get("/api/contracts")
    assert response.status_code == 401
