class TestHealthEndpoint:

    def test_health_endpoint_returns_200(self, client):
        response = client.get('/api/health')
        assert response.status_code == 200

    def test_health_endpoint_returns_json(self, client):
        response = client.get('/api/health')
        assert response.content_type.startswith('application/json')

    def test_health_endpoint_has_status_field(self, client):
        response = client.get('/api/health')
        data = response.get_json()
        assert 'status' in data
        assert data['status'] == 'healthy'

    def test_health_endpoint_reports_database_ok(self, client):
        response = client.get('/api/health')
        data = response.get_json()
        assert data['checks']['database'] == 'ok'

    def test_health_endpoint_has_timestamp_and_uptime(self, client):
        response = client.get('/api/health')
        data = response.get_json()
        assert 'timestamp' in data
        assert 'uptime_seconds' in data
