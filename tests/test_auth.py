import pytest
import json
from api.authentication.models import User, AuthToken
from datetime import datetime, timedelta

def test_register_user_success(client, auth_data):
    """Test successful user registration."""
    response = client.post('/api/auth/register', json=auth_data)
    assert response.status_code == 201
    assert response.json == {'message': 'Usuario registrado, email de verificação enviado!'}
    
    # Verify user is in the database
    user = User.objects(email=auth_data['email']).first()
    assert user is not None
    assert user.username == auth_data['username']
    
    # Verify password is hashed
    assert user._password != auth_data['password']
    assert user.check_password(auth_data['password']) is True
    
    # Verify user is inactive initially
    assert user.is_active() is False
    
    # Verify that an AuthToken was created
    token = AuthToken.objects(_user_id=str(user.id), token_type="email_verification").first()
    assert token is not None
    assert token._user_id == str(user.id)
    assert token.token_type == "email_verification"

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
        
        
def test_register_and_verify_email_success(client, auth_data):
    """Test successful email verification after registration."""
    # Register the user
    client.post('/api/auth/register', json=auth_data)
    
    # Retrieve the user and their verification token
    user = User.objects(email=auth_data['email']).first()
    token = AuthToken.objects(_user_id=str(user.id), token_type="email_verification").first()
    
    # Verify email using the token
    response = client.post('/api/auth/verify-email', json={"authToken": str(token.id)})
    assert response.status_code == 200
    assert response.json == {'message': 'Email verificado com sucesso!'}
    
    # Verify that the user is now active
    user.reload()
    assert user.is_active() is True
    assert user._is_active is True
    
def test_verify_email_invalid_token(client):
    """Test email verification with an invalid token."""
    response = client.post('/api/auth/verify-email', json={"authToken": "invalid_token"})
    assert response.status_code == 400
    assert response.json == {'error': 'Token de verificação inválido'}
    
def test_verify_email_used_token(client, auth_data):
    """Test email verification with a token that has already been used."""
    # Register the user
    client.post('/api/auth/register', json=auth_data)
    
    # Retrieve the user and their verification token
    user = User.objects(email=auth_data['email']).first()
    token = AuthToken.objects(_user_id=str(user.id), token_type="email_verification").first()
    
    # Verify email using the token (first time)
    response = client.post('/api/auth/verify-email', json={"authToken": str(token.id)})
    assert response.status_code == 200
    assert response.json == {'message': 'Email verificado com sucesso!'}
    
    
    # Try to verify email again with the same token
    response = client.post('/api/auth/verify-email', json={"authToken": str(token.id)})
    assert response.status_code == 400
    assert response.json == {'error': 'Token de verificação já utilizado'}
    
def test_verify_email_expired_token(client, auth_data, monkeypatch):
    """Test email verification with an expired token."""
    # Register the user
    client.post('/api/auth/register', json=auth_data)
    
    # Retrieve the user and their verification token
    user = User.objects(email=auth_data['email']).first()
    token = AuthToken.objects(_user_id=str(user.id), token_type="email_verification").first()
    
    # Manually expire the token
    token._expired_at = datetime.now() - timedelta(seconds=1)
    token.save()
    
    # Try to verify email using the expired token
    response = client.post('/api/auth/verify-email', json={"authToken": str(token.id)})
    assert response.status_code == 400
    assert response.json == {'error': 'Token de verificação expirado'}

def test_resend_verification_success_with_existing_token(client, auth_data):
    """Test successful resending of verification email."""
    # Register the user
    client.post('/api/auth/register', json=auth_data)
    
    # Resend verification email
    response = client.post('/api/auth/resend-verification', json={"email": auth_data['email']})
    assert response.status_code == 200
    assert response.json == {'message': 'Email de verificação reenviado com sucesso!'}
    
    # Verify that a new token was not created
    user = User.objects(email=auth_data['email']).first()
    tokens = AuthToken.objects(_user_id=str(user.id), token_type="email_verification")
    assert tokens.count() == 1  # Only one token should exist
    
def test_resend_verification_success_with_new_token(client, auth_data):
    """Test successful resending of verification email when previous token is expired."""
    # Register the user
    client.post('/api/auth/register', json=auth_data)
    
    # Retrieve the user and their verification token
    user = User.objects(email=auth_data['email']).first()
    token = AuthToken.objects(_user_id=str(user.id), token_type="email_verification").first()
    
    # Manually expire the token
    token._expired_at = datetime.now() - timedelta(seconds=1)
    token.save()

    # Resend verification email
    response = client.post('/api/auth/resend-verification', json={"email": auth_data['email']})
    assert response.status_code == 200
    assert response.json == {'message': 'Email de verificação reenviado com sucesso!'}
    
    # Verify that a new token was created
    tokens = AuthToken.objects(_user_id=str(user.id), token_type="email_verification")
    assert tokens.count() == 2  # A new token should have been created
    
def test_resend_verification_non_existent_email(client):
    """Test resending verification email to a non-existent email."""
    response = client.post('/api/auth/resend-verification', json={"email": "nonexistent@example.com"})
    assert response.status_code == 404
    assert response.json == {'error': 'Usuario não encontrado'}

def test_resend_verification_already_verified_email(client, auth_data):
    """Test resending verification email to an already verified email."""
    # Register the user
    client.post('/api/auth/register', json=auth_data)
    
    # Retrieve the user and their verification token
    user = User.objects(email=auth_data['email']).first()
    token = AuthToken.objects(_user_id=str(user.id), token_type="email_verification").first()
    
    # Verify email using the token
    client.post('/api/auth/verify-email', json={"authToken": str(token.id)})
    
    # Try to resend verification email
    response = client.post('/api/auth/resend-verification', json={"email": auth_data['email']})
    assert response.status_code == 400
    assert response.json == {'error': 'Email já verificado'}

def test_login_user_success(client, auth_data):
    """Test successful user login."""
    # Register the user first
    client.post('/api/auth/register', json=auth_data)
    
    login_data = {
        "email": auth_data['email'],
        "password": auth_data['password']
    }
    
    # Verify email to activate the user
    user = User.objects(email=auth_data['email']).first()
    token = AuthToken.objects(_user_id=str(user.id), token_type="email_verification").first()
    client.post('/api/auth/verify-email', json={"authToken": str(token.id)})
    
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
    
def test_login_user_not_verified_email(client, auth_data):
    """Test login with an unverified email."""
    # Register the user first
    client.post('/api/auth/register', json=auth_data)
    
    login_data = {
        "email": auth_data['email'],
        "password": auth_data['password']
    }
    response = client.post('/api/auth/login', json=login_data)
    assert response.status_code == 403
    assert response.json == {'error': 'Email não verificado'}

def test_register_login_and_me(client, auth_data):
    """Register a user, login and call /api/auth/me."""
    # Register (may return 201 or 400/409 if already exists)
    r = client.post('/api/auth/register', json=auth_data)
    assert r.status_code in (201, 400, 409)

    # Verify email to activate the user
    user = User.objects(email=auth_data['email']).first()
    token = AuthToken.objects(_user_id=str(user.id), token_type="email_verification").first()
    client.post('/api/auth/verify-email', json={"authToken": str(token.id)})

    # Login
    login_payload = {"email": auth_data['email'], "password": auth_data['password']}
    r = client.post('/api/auth/login', json=login_payload)
    assert r.status_code == 200
    assert 'access_token' in r.json

    token = r.json['access_token']
    headers = {'Authorization': f'Bearer {token}'}

    # me endpoint
    r = client.get('/api/auth/me', headers=headers)
    assert r.status_code == 200
    assert isinstance(r.json, dict)
    assert 'email' in r.json and r.json['email'] == auth_data['email']
    
def test_me_unauthorized(client):
    """Test /api/auth/me without authorization token."""
    r = client.get('/api/auth/me')
    assert r.status_code == 401
    assert r.json == {'msg': 'Missing Authorization Header'}
    
def test_me_invalid_token(client):
    """Test /api/auth/me with an invalid authorization token."""
    headers = {'Authorization': 'Bearer invalidtoken'}
    r = client.get('/api/auth/me', headers=headers)
    assert r.status_code == 422
    assert r.json == {'msg': 'Not enough segments'}
    
def test_me_non_existent_user(client, auth_data):
    """Test /api/auth/me with a token for a non-existent user."""
    # Register and login to get a valid token
    client.post('/api/auth/register', json=auth_data)
    login_payload = {"email": auth_data['email'], "password": auth_data['password']}
    
    # Verify email to activate the user
    user = User.objects(email=auth_data['email']).first()
    token = AuthToken.objects(_user_id=str(user.id), token_type="email_verification").first()
    client.post('/api/auth/verify-email', json={"authToken": str(token.id)})
    
    response = client.post('/api/auth/login', json=login_payload)
    token = response.json['access_token']
    
    # Manually delete the user
    user = User.objects(email=auth_data['email']).first()
    user.delete()
    
    # Call /api/auth/me with the valid token
    headers = {'Authorization': f'Bearer {token}'}
    r = client.get('/api/auth/me', headers=headers)
    assert r.status_code == 404
    assert r.json == {'error': 'Usuario não encontrado'}