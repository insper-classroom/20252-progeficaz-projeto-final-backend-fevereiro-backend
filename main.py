# Flask application setup
import json

# Environment variables
import os

# Mongo DB setup
import mongoengine as me
from dotenv import load_dotenv
from flask import Flask, jsonify, request, abort
from flask_cors import CORS

# JSON handling
from core.utils import bcrypt, jwt, update_index_json

# Load environment variables
load_dotenv()

# Init Flask app and enable CORS
app = Flask(__name__)
CORS(app)

jwt.init_app(app)
bcrypt.init_app(app)

# authentication requirements
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

# IP filtering configuration
ALLOWED_IPS = os.getenv("ALLOWED_IPS", "127.0.0.1,::1").split(",")
ALLOWED_IPS = [ip.strip() for ip in ALLOWED_IPS]  # Remove any whitespace

def get_client_ip():
    """Get the real client IP address, considering proxy headers"""
    # Check for common proxy headers
    if request.environ.get('HTTP_X_FORWARDED_FOR'):
        # X-Forwarded-For can contain multiple IPs, take the first one
        return request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0].strip()
    elif request.environ.get('HTTP_X_REAL_IP'):
        return request.environ['HTTP_X_REAL_IP']
    elif request.environ.get('HTTP_X_FORWARDED'):
        return request.environ['HTTP_X_FORWARDED']
    elif request.environ.get('HTTP_X_CLUSTER_CLIENT_IP'):
        return request.environ['HTTP_X_CLUSTER_CLIENT_IP']
    else:
        return request.environ.get('REMOTE_ADDR', '')

@app.before_request
def limit_remote_addr():
    """Filter requests by IP address"""
    client_ip = get_client_ip()
    
    # Skip IP filtering for health check endpoints to allow monitoring
    if request.endpoint and request.endpoint.startswith('health'):
        return
    
    print(f"Request from IP: {client_ip}")
    print(f"Allowed IPs: {ALLOWED_IPS}")
    
    if client_ip not in ALLOWED_IPS:
        print(f"Access denied for IP: {client_ip}")
        abort(403)  # Forbidden

# MongoDB configuration
mongodb_uri = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/forum_db")


# Connect to MongoDB
try:
    me.connect(host=mongodb_uri)
    print(f"Connected to MongoDB: {mongodb_uri}")
except Exception as e:
    print(f"Failed to connect to MongoDB: {e}")
    print("Please ensure MongoDB is running or check your MONGODB_URI in .env file")
    # You can choose to either exit or continue without DB connection
    # For development, we'll continue and let the routes handle the errors
    pass

try:
    # Update the index JSON file at startup
    update_index_json()
    print("Index JSON file updated successfully.")
except Exception as e:
    print(f"Failed to update index JSON file: {e}")

from api.authentication.routes import auth_bp  # noqa: E402
from api.health.routes import health_bp  # noqa: E402
from api.search.routes import search_bp  # noqa: E402

# Blueprints
from api.threads.routes import threads_bp  # noqa: E402

# Register blueprints
app.register_blueprint(threads_bp, url_prefix="/api")
app.register_blueprint(search_bp, url_prefix="/api")
app.register_blueprint(health_bp, url_prefix="/health")
app.register_blueprint(auth_bp, url_prefix="/api/auth")


# Global error handlers
@app.errorhandler(403)
def access_forbidden(error):
    return jsonify({"error": "Access forbidden"}), 403


@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found"}), 404


@app.errorhandler(405)
def method_not_allowed(error):
    return jsonify({"error": "Method not allowed"}), 405


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"error": "Internal server error"}), 500


# JWT error handlers
@app.errorhandler(422)
def invalid_token(error):
    return jsonify({"error": "Invalid token"}), 422


# Basic route for testing
@app.route("/")
def index():
    with open("core/index.json", "r") as f:
        index_data = json.load(f)
    return jsonify(index_data), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
