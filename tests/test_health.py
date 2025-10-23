import pytest

def test_health_endpoint(client):
    """
    Test the /health endpoint to ensure the application is running.
    """
    response = client.get('/health')
    assert response.status_code == 200 # Should now be 200 due to strict_slashes=False
    assert response.json['status'] == 'healthy' # Check the actual status field

# def test_detailed_health_endpoint(client):
#     """Test the /health/detailed endpoint."""
#     response = client.get('/health/detailed')
#     assert response.status_code == 200
#     assert 'connection' in response.json # Check for 'connection' key
#     assert 'database_operations' in response.json # Check for 'database_operations' key, as implemented in the health check logic

# TODO: Improve the above test