# Flask application setup
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_bcrypt import Bcrypt
# Mongo DB setup
import mongoengine as me



# Blueprints
from api.threads.routes import threads_bp
from api.health.routes import health_bp
from api.search.routes import search_bp
from api.authentication.routes import auth_bp

# Environment variables
import os
from dotenv import load_dotenv

# JSON handling
from core.utils import update_index_json
import json

# Load environment variables
load_dotenv()

# Init Flask app and enable CORS
app = Flask(__name__)
CORS(app)

#authentication requirements
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
bcrypt = Bcrypt(app)
jwt = JWTManager(app)

# MongoDB configuration
mongodb_uri = os.environ.get('MONGODB_URI', 'mongodb://localhost:27017/forum_db')



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

# Register blueprints
app.register_blueprint(threads_bp, url_prefix='/api')
app.register_blueprint(search_bp, url_prefix='/api')
app.register_blueprint(health_bp, url_prefix='/health')
app.register_blueprint(auth_bp, url_prefix='/api')

# Basic route for testing
@app.route('/')
def index():
    with open('core/index.json', 'r') as f:
        index_data = json.load(f)
    return jsonify(index_data), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
