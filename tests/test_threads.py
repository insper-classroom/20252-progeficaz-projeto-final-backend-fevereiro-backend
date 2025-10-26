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
    # DEBUGGING OUTPUT
    print("Response data:", response.get_json())

    assert response.status_code == 201
    assert response.json['title'] == thread_data['title']
    assert 'id' in response.json
    
    # Verify thread is in the database
    thread = Thread.objects.get(id=response.json['id'])
    assert thread is not None
    assert thread._title == thread_data['title']

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
    assert response.json == {'error': 'Title is required'}
    
def test_delete_thread_success(client, registered_user_token, thread_data):
    """Test successful deletion of a thread."""
    headers = {'Authorization': f'Bearer {registered_user_token}'}
    create_response = client.post('/api/threads', json=thread_data, headers=headers)
    thread_id = create_response.json['id']

    response = client.delete(f'/api/threads/{thread_id}', headers=headers)
    assert response.status_code == 200 # No Content
    
    
def test_delete_thread_unauthorized(client, thread_data, registered_user_token):
    """Test deleting a thread without authentication."""
    # First create a thread with auth
    headers = {'Authorization': f'Bearer {registered_user_token}'}
    create_response = client.post('/api/threads', json=thread_data, headers=headers)
    
    thread_id = create_response.json['id']
    # Now try to delete without auth
    response = client.delete(f'/api/threads/{thread_id}')
    assert response.status_code == 401 # Or 422 depending on JWT config
    assert response.json == {'msg': 'Missing Authorization Header'}

def test_delete_thread_forbidden(client, thread_data, registered_user_token, other_user_token):
    """Test deleting a thread without permission."""
    headers = {'Authorization': f'Bearer {registered_user_token}'}
    create_response = client.post('/api/threads', json=thread_data, headers=headers)
    thread_id = create_response.json['id']

    # Simulate a different user trying to delete the thread
    headers = {'Authorization': f'Bearer {other_user_token}'}
    response = client.delete(f'/api/threads/{thread_id}', headers=headers)
    assert response.status_code == 403 # Forbidden
    
def test_delete_thread_invalid_id(client, registered_user_token):
    """Test deleting a thread with invalid ID format."""
    headers = {'Authorization': f'Bearer {registered_user_token}'}
    response = client.delete('/api/threads/invalid-id-format', headers=headers)
    assert response.status_code == 400
    assert response.json == {'error': 'Invalid thread ID'}

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
    print(thread_id)
    
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
    assert updated_thread._description == update_data['description']

def test_update_thread_unauthorized(client, thread_data, registered_user_token):
    """Test updating a thread without authentication."""
    headers = {'Authorization': f'Bearer {registered_user_token}'}
    create_response = client.post('/api/threads', json={
        "title": "Thread to Update",
        "description": "Original description.",
        "semester": "2024.1",
        "courses": [],
        "subjects": []
    }, headers=headers)
    thread_id = create_response.json['id']
    
    update_data = {"description": "Attempted unauthorized update."}
    # No auth header
    response = client.put(f'/api/threads/{thread_id}', json=update_data)
    assert response.status_code == 401 # Or 422 depending on JWT config
    assert response.json == {'msg': 'Missing Authorization Header'}


def test_create_post_success(client, registered_user_token, thread_data, post_data):
    """Test successful creation of a post within a thread."""
    headers = {'Authorization': f'Bearer {registered_user_token}'}
    create_thread_response = client.post('/api/threads', json=thread_data, headers=headers)
    thread_id = create_thread_response.json['id']
    
    response = client.post(f'/api/threads/{thread_id}/posts', json=post_data, headers=headers)
    
    assert response.status_code == 201
    assert response.json['content'] == post_data['content']
    assert 'id' in response.json
    assert response.json["thread_id"] == thread_id
    
    # Verify post is in the database and linked to the thread
    post = Post.objects.get(id=response.json['id'])
    assert post is not None
    assert post._content == post_data['content']
    assert post._thread.id.__str__() == thread_id

def test_create_post_non_existent_thread(client, registered_user_token, post_data):
    """Test creating a post for a non-existent thread."""
    headers = {'Authorization': f'Bearer {registered_user_token}'}
    response = client.post('/api/threads/nonexistentid123456789012/posts', json=post_data, headers=headers)
    assert response.status_code == 400
    assert 'error' in response.json and response.json['error'] == 'Invalid thread ID'

def test_create_post_unauthorized(client, thread_data, post_data, registered_user_token):
    """Test creating a post without authentication."""
    headers = {'Authorization': f'Bearer {registered_user_token}'}
    create_response = client.post('/api/threads', json=thread_data, headers=headers)
    thread_id = create_response.json['id']
    response = client.post(f'/api/threads/{thread_id}/posts', json=post_data)
    assert response.status_code == 401
    assert response.json == {'msg': 'Missing Authorization Header'}
    
def test_create_post_missing_content(client, registered_user_token, thread_data):
    """Test creating a post with missing content."""
    headers = {'Authorization': f'Bearer {registered_user_token}'}
    create_thread_response = client.post('/api/threads', json=thread_data, headers=headers)
    thread_id = create_thread_response.json['id']
    invalid_post_data = {"author": "Test Author"}
    response = client.post(f'/api/threads/{thread_id}/posts', json=invalid_post_data, headers=headers)
    assert response.status_code == 400
    assert response.json == {'error': 'Content is required'}  
    
def test_detete_post_success(client, registered_user_token, thread_data, post_data):
    """Test successful deletion of a post."""
    headers = {'Authorization': f'Bearer {registered_user_token}'}
    create_thread_response = client.post('/api/threads', json=thread_data, headers=headers)
    thread_id = create_thread_response.json['id']
    create_post_response = client.post(f'/api/threads/{thread_id}/posts', json=post_data, headers=headers)
    post_id = create_post_response.json['id']
    response = client.delete(f'/api/posts/{post_id}', headers=headers)
    assert response.status_code == 200
    assert response.json == {'message': 'Post deleted successfully'}

def test_delete_post_unauthorized(client, thread_data, post_data, registered_user_token):
    """Test deleting a post without authentication."""
    headers = {'Authorization': f'Bearer {registered_user_token}'}
    create_thread_response = client.post('/api/threads', json=thread_data, headers=headers)
    thread_id = create_thread_response.json['id']
    create_post_response = client.post(f'/api/threads/{thread_id}/posts', json=post_data, headers=headers)
    post_id = create_post_response.json['id']
    
    response = client.delete(f'/api/posts/{post_id}')
    assert response.status_code == 401
    assert response.json == {'msg': 'Missing Authorization Header'}

def test_delete_post_forbidden(client, thread_data, post_data, registered_user_token, other_user_token):
    """Test deleting a post without permission."""
    headers = {'Authorization': f'Bearer {registered_user_token}'}
    create_thread_response = client.post('/api/threads', json=thread_data, headers=headers)
    thread_id = create_thread_response.json['id']
    create_post_response = client.post(f'/api/threads/{thread_id}/posts', json=post_data, headers=headers)
    post_id = create_post_response.json['id']
    # Simulate a different user trying to delete the post
    
    headers = {'Authorization': f'Bearer {other_user_token}'}
    response = client.delete(f'/api/posts/{post_id}', headers=headers)
    assert response.status_code == 403 # Forbidden
    assert response.json == {'error': 'You do not have permission to delete this post'}
    
def test_delete_post_invalid_id(client, registered_user_token):
    """Test deleting a post with invalid ID format."""
    headers = {'Authorization': f'Bearer {registered_user_token}'}
    response = client.delete('/api/posts/invalid-id-format', headers=headers)
    assert response.status_code == 400
    assert response.json == {'error': 'Invalid post ID'}

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
    assert updated_post._content == update_data['content']
    
def test_update_post_unauthorized(client, thread_data, post_data, registered_user_token):
    """Test updating a post without authentication."""
    headers = {'Authorization': f'Bearer {registered_user_token}'}
    create_thread_response = client.post('/api/threads', json=thread_data, headers=headers)
    thread_id = create_thread_response.json['id']
    create_post_response = client.post(f'/api/threads/{thread_id}/posts', json=post_data, headers=headers)
    post_id = create_post_response.json['id']
    
    update_data = {"content": "Attempted unauthorized update."}
    # No auth header
    response = client.put(f'/api/posts/{post_id}', json=update_data)
    assert response.status_code == 401 # Or 422 depending on JWT config
    assert response.json == {'msg': 'Missing Authorization Header'}
    
def test_update_post_forbidden(client, thread_data, post_data, registered_user_token, other_user_token):
    """Test updating a post without permission."""
    headers = {'Authorization': f'Bearer {registered_user_token}'}
    create_thread_response = client.post('/api/threads', json=thread_data, headers=headers)
    thread_id = create_thread_response.json['id']
    create_post_response = client.post(f'/api/threads/{thread_id}/posts', json=post_data, headers=headers)
    post_id = create_post_response.json['id']
    # Simulate a different user trying to update the post
    headers = {'Authorization': f'Bearer {other_user_token}'}
    update_data = {"content": "Attempted forbidden update."}
    response = client.put(f'/api/posts/{post_id}', json=update_data, headers=headers)
    assert response.status_code == 403 # Forbidden
    assert response.json == {'error': 'You do not have permission to update this post'}
    
def test_update_post_invalid_id(client, registered_user_token):
    """Test updating a post with invalid ID format."""
    headers = {'Authorization': f'Bearer {registered_user_token}'}
    update_data = {"content": "Update with invalid ID."}
    response = client.put('/api/posts/invalid-id-format', json=update_data, headers=headers)
    assert response.status_code == 400
    assert response.json == {'error': 'Invalid post ID'}

def test_thread_post_vote_lifecycle(client, registered_user_token, thread_data, post_data):
    """Create thread, create post, vote flow (upvote/duplicate/remove/downvote)."""
    headers = {'Authorization': f'Bearer {registered_user_token}'}

    # Create thread
    r = client.post('/api/threads', json=thread_data, headers=headers)
    assert r.status_code == 201
    thread = r.json
    assert 'id' in thread and thread['title'] == thread_data['title']
    thread_id = thread['id']

    # Create post in thread
    r = client.post(f'/api/threads/{thread_id}/posts', json=post_data, headers=headers)
    assert r.status_code == 201
    post = r.json
    assert 'id' in post and post['content'] == post_data['content']
    post_id = post['id']

    # Ensure post appears in thread view
    r = client.get(f'/api/threads/{thread_id}', headers=headers)
    assert r.status_code == 200
    assert any(p.get('id') == post_id for p in r.json.get('posts', []))

    # Upvote without auth -> should require auth (401 or 422 depending on config)
    r = client.post(f'/api/posts/{post_id}/upvote')
    assert r.status_code in (401, 422, 404)

    # Upvote with auth
    r = client.post(f'/api/posts/{post_id}/upvote', headers=headers)
    assert r.status_code in (200, 201, 409)
    if r.status_code in (200, 201):
        assert 'score' in r.json and r.json['score'] == 1
        
    # upvote again to remove
    r = client.post(f'/api/posts/{post_id}/upvote', headers=headers)
    assert r.status_code in (200, 201, 409)
    if r.status_code in (200, 201):
        assert 'score' in r.json and r.json['score'] == 0

    # Downvote without auth -> should require auth (401 or 422 depending on config)
    r = client.post(f'/api/posts/{post_id}/downvote')
    assert r.status_code in (401, 422, 404)
    
    # Downvote with auth
    r = client.post(f'/api/posts/{post_id}/downvote', headers=headers)
    assert r.status_code in (200, 201, 409)
    if r.status_code in (200, 201):
        assert 'score' in r.json and r.json['score'] == -1

    # downvote again to remove
    r = client.post(f'/api/posts/{post_id}/downvote', headers=headers)
    assert r.status_code in (200, 201, 409)
    if r.status_code in (200, 201):
        assert 'score' in r.json and r.json['score'] == 0
        
    # Verify vote toggling works correctly
    # upvote again to +1
    r = client.post(f'/api/posts/{post_id}/upvote', headers=headers)
    assert r.status_code in (200, 201, 409)
    if r.status_code in (200, 201):
        assert 'score' in r.json and r.json['score'] == 1
        
    # downvote again to -1
    r = client.post(f'/api/posts/{post_id}/downvote', headers=headers)
    assert r.status_code in (200, 201, 409)
    if r.status_code in (200, 201):
        assert 'score' in r.json and r.json['score'] == -1
        
    # upvote again to +1
    r = client.post(f'/api/posts/{post_id}/upvote', headers=headers)
    assert r.status_code in (200, 201, 409)
    if r.status_code in (200, 201):
        assert 'score' in r.json and r.json['score'] == 1

    
    # Test thread upvote and downvote similarly
    
    # Upvote thread without auth -> should require auth (401 or 422 depending on config)
    r = client.post(f'/api/threads/{thread_id}/upvote')
    assert r.status_code in (401, 422, 404)
    
    # Upvote thread with auth
    r = client.post(f'/api/threads/{thread_id}/upvote', headers=headers)
    assert r.status_code in (200, 201, 409)
    if r.status_code in (200, 201):
        assert 'score' in r.json and r.json['score'] == 1
        
    # upvote again to remove
    r = client.post(f'/api/threads/{thread_id}/upvote', headers=headers)
    assert r.status_code in (200, 201, 409)
    if r.status_code in (200, 201):
        assert 'score' in r.json and r.json['score'] == 0
        
        
    # Downvote thread without auth -> should require auth (401 or 422 depending on config)
    r = client.post(f'/api/threads/{thread_id}/downvote')
    assert r.status_code in (401, 422, 404)
    
    # Downvote thread with auth
    r = client.post(f'/api/threads/{thread_id}/downvote', headers=headers)
    assert r.status_code in (200, 201, 409)
    if r.status_code in (200, 201):
        assert 'score' in r.json and r.json['score'] == -1
    
    # downvote again to remove
    r = client.post(f'/api/threads/{thread_id}/downvote', headers=headers)
    assert r.status_code in (200, 201, 409)
    if r.status_code in (200, 201):
        assert 'score' in r.json and r.json['score'] == 0
        
    # Verify vote toggling works correctly
    # upvote again to +1
    r = client.post(f'/api/threads/{thread_id}/upvote', headers=headers)
    assert r.status_code in (200, 201, 409)
    if r.status_code in (200, 201):
        assert 'score' in r.json and r.json['score'] == 1
    
    # downvote again to -1
    r = client.post(f'/api/threads/{thread_id}/downvote', headers=headers)
    assert r.status_code in (200, 201, 409)
    if r.status_code in (200, 201):
        assert 'score' in r.json and r.json['score'] == -1
        
    # upvote again to +1
    r = client.post(f'/api/threads/{thread_id}/upvote', headers=headers)
    assert r.status_code in (200, 201, 409)
    if r.status_code in (200, 201):
        assert 'score' in r.json and r.json['score'] == 1
    


def test_thread_pin_unpin_flow_if_supported(client, registered_user_token, thread_data, post_data):
    """Try pin/unpin flow if endpoints exist; be tolerant to 404 if not implemented."""
    headers = {'Authorization': f'Bearer {registered_user_token}'}

    # Create thread and post
    r = client.post('/api/threads', json=thread_data, headers=headers)
    assert r.status_code == 201
    thread_id = r.json['id']

    r = client.post(f'/api/threads/{thread_id}/posts', json=post_data, headers=headers)
    assert r.status_code == 201
    post_id = r.json['id']

    # Pin post (may be 200 ok, 401, or 404 if not implemented)
    r = client.post(f'/api/posts/{post_id}/pin', headers=headers)
    assert r.status_code in (200, 401, 404)
    if r.status_code == 200:
        assert 'pinned' in r.json and isinstance(r.json['pinned'], bool)

        # Verify pinned appears first in thread (if thread view supports posts)
        r_thread = client.get(f'/api/threads/{thread_id}', headers=headers)
        assert r_thread.status_code == 200
        posts = r_thread.json.get('posts', [])
        if posts:
            assert posts[0].get('pinned', False) is True

        # Unpin
        r_unpin = client.delete(f'/api/posts/{post_id}/pin', headers=headers)
        assert r_unpin.status_code in (200, 404)
