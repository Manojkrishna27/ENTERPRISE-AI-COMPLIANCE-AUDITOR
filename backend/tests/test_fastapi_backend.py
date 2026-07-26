import uuid

def test_openapi_docs(client):
    response = client.get('/docs')
    assert response.status_code == 200
    
    openapi_response = client.get('/openapi.json')
    assert openapi_response.status_code == 200
    spec = openapi_response.json()
    assert spec['info']['title'] == 'Enterprise AI Compliance & Contract Auditor API'

def test_user_registration_and_me(client):
    unique_email = f"auditor_{uuid.uuid4().hex[:8]}@company.com"
    reg_response = client.post('/api/auth/register', json={
        "email": unique_email,
        "password": "auditorpassword123",
        "full_name": "New Auditor",
        "role": "Auditor"
    })
    assert reg_response.status_code == 201
    assert reg_response.json()["user"]["email"] == unique_email

    login_response = client.post('/api/auth/login', json={
        "email": unique_email,
        "password": "auditorpassword123"
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    me_response = client.get('/api/auth/me', headers={"Authorization": f"Bearer {token}"})
    assert me_response.status_code == 200
    assert me_response.json()["email"] == unique_email
