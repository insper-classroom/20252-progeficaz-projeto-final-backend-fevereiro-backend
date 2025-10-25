import pytest
from main import app as flask_app
import mongoengine as me
import os
from dotenv import load_dotenv
from api.authentication.models import User, AuthToken

# Load environment variables from .env for test configuration
load_dotenv()

# Use a separate test database
TEST_MONGODB_URI = os.environ.get('MONGODB_TEST', 'mongodb://localhost:27017/forum_test_db')

@pytest.fixture(scope='session')
def app():
    """
    Fixture for the Flask application.
    Configures the app for testing and uses a test database.
    """
    flask_app.config['TESTING'] = True
    flask_app.config['JWT_SECRET_KEY'] = 'test_secret_key' # Use a test secret key
    
    # Disconnect any existing connections before connecting to the test DB
    me.disconnect()
    
    # Connect to the test database
    me.connect(host=TEST_MONGODB_URI, uuidRepresentation='standard')
    print(f"\nConnected to test MongoDB: {TEST_MONGODB_URI}")
    
    yield flask_app
    
    # Clean up after all tests in the session are done
    # Drop the test database
    try:
        db = me.get_db()
        db.client.drop_database(db.name) # Correct way to drop the database
        print(f"Dropped test database: {db.name}")
    except Exception as e:
        print(f"Error dropping test database: {e}")
    finally:
        me.disconnect()
        print("Disconnected from test MongoDB.")

@pytest.fixture(scope='function')
def client(app):
    """
    Fixture for the Flask test client.
    Provides a client to make requests to the app.
    """
    with app.test_client() as client:
        yield client

@pytest.fixture(scope='function', autouse=True)
def cleanup_db_after_each_test(app):
    """
    Fixture to clean up the database after each test function.
    This ensures test isolation.
    """
    db = me.get_db()
    yield
    # Clean up all collections after each test
    for collection_name in db.list_collection_names():
        if collection_name != 'system.indexes': # Don't drop system collections like 'system.indexes'
            db.drop_collection(collection_name)

@pytest.fixture
def auth_data():
    """Fixture for common authentication data."""
    return {
        "email": "test@al.insper.edu.br",
        "username": "test",
        "password": "password123"
    }

@pytest.fixture
def registered_user_token(client, auth_data):
    """Fixture to register a user and return their JWT token."""
    # Register the user
    client.post('/api/auth/register', json=auth_data)
    
    # Verify the user's email
    user = User.objects(email=auth_data['email']).first()
    token = AuthToken.objects(_user_id=str(user.id), token_type="email_verification").first()
    client.post('/api/auth/verify-email', json={"authToken": str(token.id)})
    
    # Login the user to get their token
    login_data = {
        "email": auth_data['email'],
        "password": auth_data['password']
    }
    response = client.post('/api/auth/login', json=login_data)
    data = response.get_json()
    return data.get('access_token')

@pytest.fixture
def other_user_token(client):
    """Fixture to register a second user and return their JWT token."""
    other_user_data = {
        "email": "other@al.insper.edu.br",
        "password": "otherpassword"
    }
    # Register the other user
    client.post('/api/auth/register', json=other_user_data)
    
    # Verify the other user's email
    user = User.objects(email=other_user_data['email']).first()
    token = AuthToken.objects(_user_id=str(user.id), token_type="email_verification").first()
    client.post('/api/auth/verify-email', json={"authToken": str(token.id)})
    
    # Login the other user to get their token
    login_data = {
        "email": other_user_data['email'],
        "password": other_user_data['password']
    }
    response = client.post('/api/auth/login', json=login_data)
    data = response.get_json()
    return data.get('access_token')
