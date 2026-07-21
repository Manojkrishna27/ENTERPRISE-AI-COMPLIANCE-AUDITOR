def test_login_invalid(client):
    response = client.post('/api/auth/login', json={
        "email": "invalid@test.com",
        "password": "wrong"
    })
    assert response.status_code == 401

def test_login_success(client):
    from app.models.user import User
    from app.database import db
    user = User.query.filter_by(email="test@example.com").first()
    user.set_password("password123")
    db.session.commit()
    
    response = client.post('/api/auth/login', json={
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "access_token" in response.get_json()

def test_protected_route_missing_token(client):
    response = client.get('/api/contracts')
    assert response.status_code == 401
