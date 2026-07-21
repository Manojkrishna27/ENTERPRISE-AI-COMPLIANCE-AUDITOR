def test_health_check(client):
    response = client.get('/api/health')
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'healthy'
    assert 'uptime' in data

def test_ready_check_db_failure(client, mocker):
    mocker.patch('app.database.db.session.execute', side_effect=Exception("DB down"))
    response = client.get('/api/ready')
    # Since we don't mock Qdrant and Redis fully in this lightweight test, 
    # it might fail for multiple reasons. But it should definitely be 503.
    assert response.status_code == 503
    data = response.get_json()
    assert data['status'] == 'unhealthy'
