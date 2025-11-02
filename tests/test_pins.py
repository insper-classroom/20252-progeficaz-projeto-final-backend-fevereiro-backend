"""
Tests for the Pin/Unpin Posts system.
"""
import pytest
from api.threads.models import Thread, Post


@pytest.fixture
def thread_with_post(client, registered_user_token, thread_data, post_data):
    """Create a thread with a post for pin tests."""
    headers = {'Authorization': f'Bearer {registered_user_token}'}

    # Create thread
    thread_response = client.post('/api/threads', json=thread_data, headers=headers)
    thread_id = thread_response.json['id']

    # Create post
    post_response = client.post(f'/api/threads/{thread_id}/posts', json=post_data, headers=headers)
    post_id = post_response.json['id']

    return {
        'thread_id': thread_id,
        'post_id': post_id,
        'thread_owner_token': registered_user_token
    }


@pytest.fixture
def multiple_posts_in_thread(client, registered_user_token, thread_data):
    """Create a thread with multiple posts for ordering tests."""
    headers = {'Authorization': f'Bearer {registered_user_token}'}

    # Create thread
    thread_response = client.post('/api/threads', json=thread_data, headers=headers)
    thread_id = thread_response.json['id']

    # Create multiple posts
    post_ids = []
    for i in range(3):
        post_response = client.post(
            f'/api/threads/{thread_id}/posts',
            json={'content': f'Post content {i}'},
            headers=headers
        )
        post_ids.append(post_response.json['id'])

    return {
        'thread_id': thread_id,
        'post_ids': post_ids,
        'thread_owner_token': registered_user_token
    }


class TestPinPost:
    """Tests for pinning posts."""

    def test_pin_post_success(self, client, thread_with_post):
        """Test successful pinning of a post."""
        headers = {'Authorization': f'Bearer {thread_with_post["thread_owner_token"]}'}
        post_id = thread_with_post['post_id']

        response = client.post(f'/api/posts/{post_id}/pin', headers=headers)
        assert response.status_code == 200
        assert 'pinned' in response.json
        assert response.json['pinned'] is True
        assert 'message' in response.json

    def test_pin_post_shows_in_thread(self, client, thread_with_post):
        """Test that pinned post shows as pinned in thread."""
        headers = {'Authorization': f'Bearer {thread_with_post["thread_owner_token"]}'}
        thread_id = thread_with_post['thread_id']
        post_id = thread_with_post['post_id']

        # Pin post
        client.post(f'/api/posts/{post_id}/pin', headers=headers)

        # Get thread
        response = client.get(f'/api/threads/{thread_id}', headers=headers)
        assert response.status_code == 200

        # Find the post in thread
        posts = response.json.get('posts', [])
        pinned_post = next((p for p in posts if p['id'] == post_id), None)
        assert pinned_post is not None
        assert pinned_post['pinned'] is True

    def test_pin_post_appears_first(self, client, multiple_posts_in_thread):
        """Test that pinned posts appear first in the list."""
        headers = {'Authorization': f'Bearer {multiple_posts_in_thread["thread_owner_token"]}'}
        thread_id = multiple_posts_in_thread['thread_id']
        post_ids = multiple_posts_in_thread['post_ids']

        # Pin the last post
        client.post(f'/api/posts/{post_ids[2]}/pin', headers=headers)

        # Get thread
        response = client.get(f'/api/threads/{thread_id}', headers=headers)
        posts = response.json['posts']

        # Pinned post should be first
        assert posts[0]['id'] == post_ids[2]
        assert posts[0]['pinned'] is True

    def test_pin_post_by_non_owner_forbidden(self, client, thread_with_post, other_user_token):
        """Test that non-owner cannot pin post."""
        headers = {'Authorization': f'Bearer {other_user_token}'}
        post_id = thread_with_post['post_id']

        response = client.post(f'/api/posts/{post_id}/pin', headers=headers)
        assert response.status_code == 403

    def test_pin_post_unauthorized(self, client, thread_with_post):
        """Test pinning without authentication."""
        post_id = thread_with_post['post_id']
        response = client.post(f'/api/posts/{post_id}/pin')
        assert response.status_code == 401
        assert response.json == {'msg': 'Missing Authorization Header'}

    def test_pin_non_existent_post(self, client, registered_user_token):
        """Test pinning non-existent post."""
        headers = {'Authorization': f'Bearer {registered_user_token}'}
        response = client.post('/api/posts/507f1f77bcf86cd799439011/pin', headers=headers)
        assert response.status_code == 404

    def test_pin_post_invalid_id(self, client, registered_user_token):
        """Test pinning with invalid post ID."""
        headers = {'Authorization': f'Bearer {registered_user_token}'}
        response = client.post('/api/posts/invalid-id/pin', headers=headers)
        assert response.status_code == 400

    def test_pin_already_pinned_post(self, client, thread_with_post):
        """Test pinning an already pinned post (should be idempotent)."""
        headers = {'Authorization': f'Bearer {thread_with_post["thread_owner_token"]}'}
        post_id = thread_with_post['post_id']

        # Pin once
        response1 = client.post(f'/api/posts/{post_id}/pin', headers=headers)
        assert response1.status_code == 200
        assert response1.json['pinned'] is True

        # Pin again
        response2 = client.post(f'/api/posts/{post_id}/pin', headers=headers)
        assert response2.status_code == 200
        assert response2.json['pinned'] is True


class TestUnpinPost:
    """Tests for unpinning posts."""

    def test_unpin_post_success(self, client, thread_with_post):
        """Test successful unpinning of a post."""
        headers = {'Authorization': f'Bearer {thread_with_post["thread_owner_token"]}'}
        post_id = thread_with_post['post_id']

        # Pin first
        client.post(f'/api/posts/{post_id}/pin', headers=headers)

        # Unpin
        response = client.delete(f'/api/posts/{post_id}/pin', headers=headers)
        assert response.status_code == 200
        assert 'pinned' in response.json
        assert response.json['pinned'] is False

    def test_unpin_post_shows_in_thread(self, client, thread_with_post):
        """Test that unpinned post shows as not pinned in thread."""
        headers = {'Authorization': f'Bearer {thread_with_post["thread_owner_token"]}'}
        thread_id = thread_with_post['thread_id']
        post_id = thread_with_post['post_id']

        # Pin then unpin
        client.post(f'/api/posts/{post_id}/pin', headers=headers)
        client.delete(f'/api/posts/{post_id}/pin', headers=headers)

        # Get thread
        response = client.get(f'/api/threads/{thread_id}', headers=headers)
        posts = response.json['posts']

        # Find the post
        unpinned_post = next((p for p in posts if p['id'] == post_id), None)
        assert unpinned_post is not None
        assert unpinned_post['pinned'] is False

    def test_unpin_post_by_non_owner_forbidden(self, client, thread_with_post, other_user_token):
        """Test that non-owner cannot unpin post."""
        headers_owner = {'Authorization': f'Bearer {thread_with_post["thread_owner_token"]}'}
        headers_other = {'Authorization': f'Bearer {other_user_token}'}
        post_id = thread_with_post['post_id']

        # Pin as owner
        client.post(f'/api/posts/{post_id}/pin', headers=headers_owner)

        # Try to unpin as non-owner
        response = client.delete(f'/api/posts/{post_id}/pin', headers=headers_other)
        assert response.status_code == 403

    def test_unpin_post_unauthorized(self, client, thread_with_post):
        """Test unpinning without authentication."""
        headers = {'Authorization': f'Bearer {thread_with_post["thread_owner_token"]}'}
        post_id = thread_with_post['post_id']

        # Pin first
        client.post(f'/api/posts/{post_id}/pin', headers=headers)

        # Try to unpin without auth
        response = client.delete(f'/api/posts/{post_id}/pin')
        assert response.status_code == 401

    def test_unpin_already_unpinned_post(self, client, thread_with_post):
        """Test unpinning an already unpinned post (should be idempotent)."""
        headers = {'Authorization': f'Bearer {thread_with_post["thread_owner_token"]}'}
        post_id = thread_with_post['post_id']

        # Unpin when not pinned
        response = client.delete(f'/api/posts/{post_id}/pin', headers=headers)
        assert response.status_code == 200
        assert response.json['pinned'] is False


class TestMultiplePinnedPosts:
    """Tests for multiple pinned posts."""

    def test_pin_multiple_posts(self, client, multiple_posts_in_thread):
        """Test pinning multiple posts."""
        headers = {'Authorization': f'Bearer {multiple_posts_in_thread["thread_owner_token"]}'}
        thread_id = multiple_posts_in_thread['thread_id']
        post_ids = multiple_posts_in_thread['post_ids']

        # Pin first and third posts
        client.post(f'/api/posts/{post_ids[0]}/pin', headers=headers)
        client.post(f'/api/posts/{post_ids[2]}/pin', headers=headers)

        # Get thread
        response = client.get(f'/api/threads/{thread_id}', headers=headers)
        posts = response.json['posts']

        # Both should be pinned and appear first
        pinned_posts = [p for p in posts if p['pinned']]
        assert len(pinned_posts) == 2

        # First two posts in list should be the pinned ones
        assert posts[0]['pinned'] is True
        assert posts[1]['pinned'] is True
        assert posts[2]['pinned'] is False

    def test_pinned_posts_ordered_by_score(self, client, multiple_posts_in_thread, other_user_token):
        """Test that pinned posts are ordered by score among themselves."""
        headers_owner = {'Authorization': f'Bearer {multiple_posts_in_thread["thread_owner_token"]}'}
        headers_other = {'Authorization': f'Bearer {other_user_token}'}
        thread_id = multiple_posts_in_thread['thread_id']
        post_ids = multiple_posts_in_thread['post_ids']

        # Pin all posts
        for post_id in post_ids:
            client.post(f'/api/posts/{post_id}/pin', headers=headers_owner)

        # Upvote first post (should have highest score)
        client.post(f'/api/posts/{post_ids[0]}/upvote', headers=headers_other)

        # Get thread
        response = client.get(f'/api/threads/{thread_id}', headers=headers_owner)
        posts = response.json['posts']

        # First post should be the one with highest score
        assert posts[0]['id'] == post_ids[0]
        assert posts[0]['score'] == 1


class TestPinPostIntegration:
    """Integration tests for pin/unpin functionality."""

    def test_pin_unpin_lifecycle(self, client, thread_with_post):
        """Test complete pin/unpin lifecycle."""
        headers = {'Authorization': f'Bearer {thread_with_post["thread_owner_token"]}'}
        post_id = thread_with_post['post_id']

        # Initially not pinned
        response1 = client.get(f'/api/posts/{post_id}', headers=headers)
        assert response1.json['pinned'] is False

        # Pin it
        response2 = client.post(f'/api/posts/{post_id}/pin', headers=headers)
        assert response2.json['pinned'] is True

        # Verify pinned
        response3 = client.get(f'/api/posts/{post_id}', headers=headers)
        assert response3.json['pinned'] is True

        # Unpin it
        response4 = client.delete(f'/api/posts/{post_id}/pin', headers=headers)
        assert response4.json['pinned'] is False

        # Verify unpinned
        response5 = client.get(f'/api/posts/{post_id}', headers=headers)
        assert response5.json['pinned'] is False

    def test_pin_persists_across_requests(self, client, thread_with_post):
        """Test that pin status persists."""
        headers = {'Authorization': f'Bearer {thread_with_post["thread_owner_token"]}'}
        thread_id = thread_with_post['thread_id']
        post_id = thread_with_post['post_id']

        # Pin post
        client.post(f'/api/posts/{post_id}/pin', headers=headers)

        # Get thread in multiple requests
        for _ in range(3):
            response = client.get(f'/api/threads/{thread_id}', headers=headers)
            pinned_post = next((p for p in response.json['posts'] if p['id'] == post_id), None)
            assert pinned_post['pinned'] is True

    def test_delete_pinned_post_succeeds(self, client, thread_with_post):
        """Test that pinned post can be deleted."""
        headers = {'Authorization': f'Bearer {thread_with_post["thread_owner_token"]}'}
        post_id = thread_with_post['post_id']

        # Pin post
        client.post(f'/api/posts/{post_id}/pin', headers=headers)

        # Delete post
        response = client.delete(f'/api/posts/{post_id}', headers=headers)
        assert response.status_code == 200

    def test_pin_status_in_post_list(self, client, multiple_posts_in_thread):
        """Test that pin status is correctly shown in post lists."""
        headers = {'Authorization': f'Bearer {multiple_posts_in_thread["thread_owner_token"]}'}
        thread_id = multiple_posts_in_thread['thread_id']
        post_ids = multiple_posts_in_thread['post_ids']

        # Pin middle post
        client.post(f'/api/posts/{post_ids[1]}/pin', headers=headers)

        # Get thread
        response = client.get(f'/api/threads/{thread_id}', headers=headers)
        posts = response.json['posts']

        # Verify correct pin statuses
        for post in posts:
            if post['id'] == post_ids[1]:
                assert post['pinned'] is True
            else:
                assert post['pinned'] is False


class TestPinPostEdgeCases:
    """Edge cases for pin/unpin."""

    def test_post_author_can_pin_if_thread_owner(self, client, registered_user_token, thread_data, post_data):
        """Test that post author who is also thread owner can pin their post."""
        headers = {'Authorization': f'Bearer {registered_user_token}'}

        # Create thread
        thread_response = client.post('/api/threads', json=thread_data, headers=headers)
        thread_id = thread_response.json['id']

        # Create post (same user)
        post_response = client.post(f'/api/threads/{thread_id}/posts', json=post_data, headers=headers)
        post_id = post_response.json['id']

        # Pin own post
        response = client.post(f'/api/posts/{post_id}/pin', headers=headers)
        assert response.status_code == 200

    def test_post_author_cannot_pin_if_not_thread_owner(self, client, registered_user_token, other_user_token, thread_data, post_data):
        """Test that post author cannot pin if not thread owner."""
        headers_owner = {'Authorization': f'Bearer {registered_user_token}'}
        headers_author = {'Authorization': f'Bearer {other_user_token}'}

        # Thread owner creates thread
        thread_response = client.post('/api/threads', json=thread_data, headers=headers_owner)
        thread_id = thread_response.json['id']

        # Different user creates post
        post_response = client.post(f'/api/threads/{thread_id}/posts', json=post_data, headers=headers_author)
        post_id = post_response.json['id']

        # Post author tries to pin (should fail)
        response = client.post(f'/api/posts/{post_id}/pin', headers=headers_author)
        assert response.status_code == 403
