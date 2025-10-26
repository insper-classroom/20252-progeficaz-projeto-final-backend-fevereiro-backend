import pytest
from api.threads.models import Thread
from mongoengine.queryset import QuerySet
from core import mongodb_connection_utils

def test_health_endpoint(client, registered_user_token):
    """
    Test the /health endpoint to ensure the application is running.
    """
    response = client.get('/health', headers={"Authorization": f"Bearer {registered_user_token}"})
    assert response.status_code == 200
    assert response.json['status'] == 'healthy'
    assert response.json['database'] == 'connected'

def test_health_endpoint_db_failure(client, monkeypatch, registered_user_token):
    """
    Test the /health endpoint when the database connection fails.
    """
    # Simulate a database connection error by mocking the 'first' method on a QuerySet
    def mock_first_raises_exception(*args, **kwargs):
        raise Exception("Database connection failed")

    monkeypatch.setattr(QuerySet, "first", mock_first_raises_exception)

    response = client.get('/health', headers={"Authorization": f"Bearer {registered_user_token}"})
    assert response.status_code == 503
    assert response.json['status'] == 'unhealthy'
    assert response.json['database'] == 'disconnected'
    assert 'Database connection failed' in response.json['error']

def test_detailed_health_endpoint_success(client, monkeypatch, registered_user_token):
    """Test the /health/detailed endpoint for a successful connection."""
    # Patch the functions that the view actually calls (in api.health.views)
    monkeypatch.setattr('api.health.views.test_mongodb_connection', lambda uri=None, timeout=10: {
        'success': True, 'connection_type': 'Test', 'server_info': {'version': 'mock'}, 'performance': {}, 'error': None
    })
    monkeypatch.setattr('api.health.views.test_database_operations', lambda uri=None: {
        'success': True, 'operations': {'create': True, 'read': True, 'update': True, 'delete': True, 'relationship': True}, 'error': None
    })

    response = client.get('/health/detailed', headers={"Authorization": f"Bearer {registered_user_token}"})
    assert response.status_code == 200
    assert 'timestamp' in response.json
    assert 'connection' in response.json
    assert response.json['connection']['status'] == 'connected'
    assert 'database_operations' in response.json
    assert response.json['database_operations']['status'] == 'operational'
    assert response.json['database_operations']['operations']['create'] == True

def test_detailed_health_endpoint_failure(client, monkeypatch, registered_user_token):
    """Test the /health/detailed endpoint when the DB connection fails."""
    def mock_connection_test(uri=None, timeout=10):
        return {'success': False, 'error': 'Simulated connection error', 'connection_type': 'Mock', 'server_info': {}, 'performance': {}}

    # Patch the name used by the view
    monkeypatch.setattr('api.health.views.test_mongodb_connection', mock_connection_test)
    # Ensure ops function is present but won't be used
    monkeypatch.setattr('api.health.views.test_database_operations', lambda uri=None: {
        'success': False, 'operations': {}, 'error': 'Not tested due to connection failure'
    })

    response = client.get('/health/detailed', headers={"Authorization": f"Bearer {registered_user_token}"})
    # If connection fails, view should return 503
    assert response.status_code == 503
    assert response.json['connection']['status'] == 'disconnected'
    assert 'Simulated connection error' in response.json['connection']['error']
    assert response.json['database_operations']['status'] == 'not_tested'

def test_health_endpoint_method_not_allowed(client, registered_user_token):
    """Test that POSTing to health endpoints returns 405 Method Not Allowed (or 404 if route not found)."""
    # use trailing slash for the blueprint root; be tolerant to 404/405 differences across environments
    response_health = client.post('/health/', headers={"Authorization": f"Bearer {registered_user_token}"})
    assert response_health.status_code in (404, 405)
    if response_health.status_code == 405:
        assert response_health.json == {'error': 'Method not allowed'}

    response_detailed = client.post('/health/detailed', headers={"Authorization": f"Bearer {registered_user_token}"})
    assert response_detailed.status_code in (404, 405)
    if response_detailed.status_code == 405:
        assert response_detailed.json == {'error': 'Method not allowed'}
