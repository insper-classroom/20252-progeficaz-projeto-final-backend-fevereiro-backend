from flask import Flask
from flask_cors import CORS
import os
import mongoengine as me
from datetime import datetime
from models import Thread, Post, get_brasilia_now
from dotenv import load_dotenv
import pytz

# Load environment variables
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # MongoDB configuration
    mongodb_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/forum_db')
    
    try:
        me.connect(host=mongodb_uri)
        print(f"Connected to MongoDB: {mongodb_uri}")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        print("Please ensure MongoDB is running or check your MONGODB_URI in .env file")
        # You can choose to either exit or continue without DB connection
        # For development, we'll continue and let the routes handle the errors
        pass

    CORS(app)

    from routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    @app.route('/')
    def index():
        return {'message': 'working'}

    @app.route('/health')
    def health():
        """Health check endpoint to verify DB connection"""
        try:
            # Try to perform a simple operation to check DB connection
            Thread.objects().limit(1)
            return {'status': 'healthy', 'database': 'connected'}
        except Exception as e:
            return {'status': 'unhealthy', 'database': 'disconnected', 'error': str(e)}, 503

    @app.route('/health/detailed')
    def detailed_health():
        """Detailed health check with MongoDB connection test"""
        from mongodb_connection_utils import test_mongodb_connection, test_database_operations
        
        # Test connection
        conn_result = test_mongodb_connection()
        
        response = {
            'timestamp': get_brasilia_now().isoformat(),
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

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
