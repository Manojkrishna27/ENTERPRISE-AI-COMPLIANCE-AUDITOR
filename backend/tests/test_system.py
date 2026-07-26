def test_health_check(client):
    response = client.get('/api/health')
    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'healthy'
    assert 'uptime' in data

def test_ready_check(client):
    response = client.get('/api/ready')
    # Will return 200 if dependencies connected or 503 if redis/qdrant unavailable in local unit test environment
    assert response.status_code in [200, 503]
    data = response.json()
    assert "status" in data
    assert "backend" in data
