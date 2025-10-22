import pytest
import json
from api.threads.models import Thread, Post
from api.authentication.models import User

@pytest.fixture
def thread_data():
    """Fixture for common thread data."""
    return {
        "title": "My Test Thread",
        "description": "This is a detailed description for the test thread.",
        "semester": "2024.1",
        "courses": ["COMP123", "MAT456"],
        "subjects": ["Programming", "Algorithms"]
    }

@pytest.fixture
def post_data():
    """Fixture for common post data."""
    return {
        "author": "Test Author",
        "content": "This is the content of a test post."
    }

def test_create_thread_success(client, registered_user_token, thread_data):
    """Test successful creation of a thread."""
    headers = {'Authorization': f'Bearer {registered_user_token}'}
    response = client.post('/api/threads', json=thread_data, headers=headers)
    
    assert response.status_code == 201
    assert response.json['title'] == thread_data['title']
    assert 'id' in response.json
    
    # Verify thread is in the database
    thread = Thread.objects.get(id=response.json['id'])
    assert thread is not None
    assert thread.title == thread_data['title']

def test_create_thread_unauthorized(client, thread_data):
    """Test creating a thread without authentication."""
    response = client.post('/api/threads', json=thread_data)
    assert response.status_code == 401 # Or 422 depending on JWT config
    assert response.json == {'msg': 'Missing Authorization Header'}

def test_create_thread_missing_title(client, registered_user_token, thread_data):
    """Test creating a thread with missing title."""
    headers = {'Authorization': f'Bearer {registered_user_token}'}
    invalid_data = thread_data.copy()
    del invalid_data['title']
    response = client.post('/api/threads', json=invalid_data, headers=headers)
    assert response.status_code == 400
    assert response.json['details']['title'] == 'Title is required'

def test_get_all_threads(client, registered_user_token, thread_data):
    """Test retrieving all threads."""
    headers = {'Authorization': f'Bearer {registered_user_token}'}
    client.post('/api/threads', json=thread_data, headers=headers) # Create one thread
    
    response = client.get('/api/threads', headers=headers)
    assert response.status_code == 200
    assert 'threads' in response.json
    assert len(response.json['threads']) == 1
    assert response.json['threads'][0]['title'] == thread_data['title']

def test_get_single_thread(client, registered_user_token, thread_data):
    """Test retrieving a single thread by ID."""
    headers = {'Authorization': f'Bearer {registered_user_token}'}
    create_response = client.post('/api/threads', json=thread_data, headers=headers)
    thread_id = create_response.json['id']
    
    response = client.get(f'/api/threads/{thread_id}', headers=headers)
    assert response.status_code == 200
    assert response.json['id'] == thread_id
    assert response.json['title'] == thread_data['title']
    assert 'posts' in response.json # Should include posts list (even if empty)

def test_get_non_existent_thread(client, registered_user_token):
    """Test retrieving a non-existent thread."""
    headers = {'Authorization': f'Bearer {registered_user_token}'}
    response = client.get('/api/threads/nonexistentid123456789012', headers=headers)
    assert response.status_code == 400
    assert 'error' in response.json and response.json['error'] == 'Invalid thread ID'

def test_update_thread_success(client, registered_user_token, thread_data):
    """Test successful update of a thread."""
    headers = {'Authorization': f'Bearer {registered_user_token}'}
    create_response = client.post('/api/threads', json=thread_data, headers=headers)
    thread_id = create_response.json['id']
    
    update_data = {"description": "An updated description for the thread."}
    response = client.put(f'/api/threads/{thread_id}', json=update_data, headers=headers)
    
    assert response.status_code == 201
    assert response.json['message'] == "Thread updated successfully"
    
    # Verify update in DB
    updated_thread = Thread.objects.get(id=thread_id)
    assert updated_thread.description == update_data['description']

def test_update_thread_unauthorized(client, thread_data):
    """Test updating a thread without authentication."""
    # Create a thread first (e.g., by another user or without auth for simplicity)
    # We need a valid user to create the thread to test updating it without auth.
    # The Thread model does not have an 'author' field, so we just need to create a thread.
    # The User creation was failing because 'name' and 'matricula' are required.
    # However, we don't even need to create a user for this test.
    # Just create a thread directly.
    thread = Thread(title="Unauthorized Thread", description="Desc").save()
    response = client.put(f'/api/threads/{thread.id}', json={"title": "New Title"})
    assert response.status_code == 401

def test_create_post_success(client, registered_user_token, thread_data, post_data):
    """Test successful creation of a post within a thread."""
    headers = {'Authorization': f'Bearer {registered_user_token}'}
    create_thread_response = client.post('/api/threads', json=thread_data, headers=headers)
    thread_id = create_thread_response.json['id']
    
    response = client.post(f'/api/threads/{thread_id}/posts', json=post_data, headers=headers)
    
    assert response.status_code == 201
    assert response.json['content'] == post_data['content']
    assert 'id' in response.json
    assert response.json['thread'] == thread_id
    
    # Verify post is in the database and linked to the thread
    post = Post.objects.get(id=response.json['id'])
    assert post is not None
    assert post.content == post_data['content']
    assert post.thread.id == thread_id

def test_create_post_non_existent_thread(client, registered_user_token, post_data):
    """Test creating a post for a non-existent thread."""
    headers = {'Authorization': f'Bearer {registered_user_token}'}
    response = client.post('/api/threads/nonexistentid123456789012/posts', json=post_data, headers=headers)
    assert response.status_code == 400
    assert 'error' in response.json and response.json['error'] == 'Invalid thread ID'

def test_get_single_post(client, registered_user_token, thread_data, post_data):
    """Test retrieving a single post by ID."""
    headers = {'Authorization': f'Bearer {registered_user_token}'}
    create_thread_response = client.post('/api/threads', json=thread_data, headers=headers)
    thread_id = create_thread_response.json['id']
    create_post_response = client.post(f'/api/threads/{thread_id}/posts', json=post_data, headers=headers)
    post_id = create_post_response.json['id']
    
    response = client.get(f'/api/posts/{post_id}', headers=headers)
    assert response.status_code == 200
    assert response.json['id'] == post_id
    assert response.json['content'] == post_data['content']

def test_update_post_success(client, registered_user_token, thread_data, post_data):
    """Test successful update of a post."""
    headers = {'Authorization': f'Bearer {registered_user_token}'}
    create_thread_response = client.post('/api/threads', json=thread_data, headers=headers)
    thread_id = create_thread_response.json['id']
    create_post_response = client.post(f'/api/threads/{thread_id}/posts', json=post_data, headers=headers)
    post_id = create_post_response.json['id']
    
    update_data = {"content": "Updated content for the test post."}
    response = client.put(f'/api/posts/{post_id}', json=update_data, headers=headers)
    
    assert response.status_code == 201
    assert response.json['message'] == "Post updated successfully"
    
    # Verify update in DB
    updated_post = Post.objects.get(id=post_id)
    assert updated_post.content == update_data['content']
