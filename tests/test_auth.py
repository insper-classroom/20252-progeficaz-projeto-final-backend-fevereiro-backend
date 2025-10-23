import pytest
import json
from api.authentication.models import User

def test_register_user_success(client, auth_data):
    """Test successful user registration."""
    response = client.post('/api/auth/register', json=auth_data)
    assert response.status_code == 201
    assert response.json == {'message': 'Usuario registrado com sucesso!'}
    
    # Verify user is in the database
    user = User.objects(email=auth_data['email']).first()
    assert user is not None
    assert user.username == auth_data['username']

def test_register_user_existing_email(client, auth_data):
    """Test registration with an email that already exists."""
    # First, register the user successfully
    client.post('/api/auth/register', json=auth_data)
    
    # Try to register again with the same email
    response = client.post('/api/auth/register', json=auth_data)
    assert response.status_code == 400
    assert response.json == {'error': 'Usuario ja existe'}

def test_register_user_invalid_insper_email(client, auth_data):
    """Test registration with an email not ending in @al.insper.edu.br."""
    invalid_data = auth_data.copy()
    invalid_data['email'] = 'test@example.com'
    response = client.post('/api/auth/register', json=invalid_data)
    assert response.status_code == 422
    assert response.json == {'error': 'Email deve ser do Insper'}
def test_register_user_missing_fields(client, auth_data):
    """Test registration with missing required fields."""
    required_fields = ["email", "password"]
    for field_to_remove in required_fields:
        data_with_missing_field = auth_data.copy()
        del data_with_missing_field[field_to_remove]
        response = client.post('/api/auth/register', json=data_with_missing_field)
        assert response.status_code == 400
        assert response.json == {'error': 'Campos obrigatórios: email, username, password'}

def test_login_user_success(client, auth_data):
    """Test successful user login."""
    # Register the user first
    client.post('/api/auth/register', json=auth_data)
    
    login_data = {
        "email": auth_data['email'],
        "password": auth_data['password']
    }
    response = client.post('/api/auth/login', json=login_data)
    assert response.status_code == 200
    assert 'access_token' in response.json

def test_login_user_incorrect_password(client, auth_data):
    """Test login with incorrect password."""
    # Register the user first
    client.post('/api/auth/register', json=auth_data)
    
    login_data = {
        "email": auth_data['email'],
        "password": "wrongpassword"
    }
    response = client.post('/api/auth/login', json=login_data)
    assert response.status_code == 401
    assert response.json == {'error': 'Email ou senha inválidos'}

def test_login_user_non_existent_email(client, auth_data):
    """Test login with a email that does not exist."""
    login_data = {
        "email": "nonexistentuser@example.com",
        "password": auth_data['password']
    }
    response = client.post('/api/auth/login', json=login_data)
    assert response.status_code == 401
    assert response.json == {'error': 'Email ou senha inválidos'}
