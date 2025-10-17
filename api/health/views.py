import pytz
from api.threads.models import Thread
from core.mongodb_connection_utils import test_mongodb_connection, test_database_operations
from datetime import datetime
from core.utils import utc_to_brasilia
from core.types import api_response

def health() -> api_response:
    try:
        # Try to perform a simple operation to check DB connection
        Thread.objects().limit(1)
        return {'status': 'healthy', 'database': 'connected'}
    except Exception as e:
        return {'status': 'unhealthy', 'database': 'disconnected', 'error': str(e)}, 503

def detailed_health() -> api_response:
    # Test connection
    conn_result = test_mongodb_connection()
    
    response = {
        'timestamp': utc_to_brasilia(datetime.now(pytz.UTC).replace(tzinfo=None)).isoformat(),
        'connection': {
            'status': 'connected' if conn_result['success'] else 'disconnected',
            'type': conn_result['connection_type'],
            'server_version': conn_result['server_info'].get('version', 'Unknown') if conn_result['success'] else None,
            'performance': conn_result['performance'] if conn_result['success'] else None,
            'error': conn_result['error'] if not conn_result['success'] else None
        }
    }
    
    if conn_result['success']:
        # Test database operations if connection is successful
        ops_result = test_database_operations()
        response['database_operations'] = {
            'status': 'operational' if ops_result['success'] else 'failed',
            'operations': ops_result['operations'],
            'error': ops_result['error'] if not ops_result['success'] else None
        }
        status_code = 200
    else:
        response['database_operations'] = {'status': 'not_tested', 'reason': 'connection_failed'}
        status_code = 503
    
    return response, status_code