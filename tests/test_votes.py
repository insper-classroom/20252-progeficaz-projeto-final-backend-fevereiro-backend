"""
Tests for the Voting system (upvote/downvote for threads and posts).
"""
import pytest
from api.threads.models import Thread, Post
from api.authentication.models import User


@pytest.fixture
def thread_for_voting(client, registered_user_token, thread_data):
    """Create a thread for voting tests."""
    headers = {'Authorization': f'Bearer {registered_user_token}'}
    response = client.post('/api/threads', json=thread_data, headers=headers)
    assert response.status_code == 201
    return response.json['id']


@pytest.fixture
def post_for_voting(client, registered_user_token, thread_data, post_data):
    """Create a post for voting tests."""
    headers = {'Authorization': f'Bearer {registered_user_token}'}

    # Create thread
    thread_response = client.post('/api/threads', json=thread_data, headers=headers)
    thread_id = thread_response.json['id']

    # Create post
    post_response = client.post(f'/api/threads/{thread_id}/posts', json=post_data, headers=headers)
    assert post_response.status_code == 201
    return post_response.json['id']


class TestThreadUpvote:
    """Tests for upvoting threads."""

    def test_upvote_thread_success(self, client, other_user_token, thread_for_voting):
        """Test successful upvote of a thread."""
        headers = {'Authorization': f'Bearer {other_user_token}'}
        response = client.post(f'/api/threads/{thread_for_voting}/upvote', headers=headers)

        assert response.status_code == 201
        assert 'score' in response.json
        assert response.json['score'] == 1
        assert 'message' in response.json

    def test_upvote_thread_increases_score(self, client, other_user_token, thread_for_voting):
        """Test that upvoting increases thread score."""
        headers = {'Authorization': f'Bearer {other_user_token}'}

        # Get initial thread
        get_response = client.get(f'/api/threads/{thread_for_voting}', headers=headers)
        initial_score = get_response.json.get('score', 0)

        # Upvote
        vote_response = client.post(f'/api/threads/{thread_for_voting}/upvote', headers=headers)
        assert vote_response.status_code == 201

        # Verify score increased
        get_response = client.get(f'/api/threads/{thread_for_voting}', headers=headers)
        new_score = get_response.json['score']
        assert new_score == initial_score + 1

    def test_upvote_thread_toggle_removes_vote(self, client, other_user_token, thread_for_voting):
        """Test that upvoting twice toggles the vote (removes it)."""
        headers = {'Authorization': f'Bearer {other_user_token}'}

        # First upvote
        response1 = client.post(f'/api/threads/{thread_for_voting}/upvote', headers=headers)
        assert response1.status_code == 201
        assert response1.json['score'] == 1

        # Second upvote (toggle off)
        response2 = client.post(f'/api/threads/{thread_for_voting}/upvote', headers=headers)
        assert response2.status_code == 201
        assert response2.json['score'] == 0

    def test_upvote_thread_after_downvote_changes_vote(self, client, other_user_token, thread_for_voting):
        """Test that upvoting after downvote changes the vote."""
        headers = {'Authorization': f'Bearer {other_user_token}'}

        # Downvote first
        response1 = client.post(f'/api/threads/{thread_for_voting}/downvote', headers=headers)
        assert response1.status_code == 201
        assert response1.json['score'] == -1

        # Then upvote (should change from downvote to upvote)
        response2 = client.post(f'/api/threads/{thread_for_voting}/upvote', headers=headers)
        assert response2.status_code == 201
        assert response2.json['score'] == 1

    def test_upvote_thread_unauthorized(self, client, thread_for_voting):
        """Test upvoting without authentication."""
        response = client.post(f'/api/threads/{thread_for_voting}/upvote')
        assert response.status_code == 401
        assert response.json == {'msg': 'Missing Authorization Header'}

    def test_upvote_non_existent_thread(self, client, registered_user_token):
        """Test upvoting a non-existent thread."""
        headers = {'Authorization': f'Bearer {registered_user_token}'}
        response = client.post('/api/threads/507f1f77bcf86cd799439011/upvote', headers=headers)
        assert response.status_code == 404

    def test_upvote_thread_invalid_id(self, client, registered_user_token):
        """Test upvoting with invalid thread ID."""
        headers = {'Authorization': f'Bearer {registered_user_token}'}
        response = client.post('/api/threads/invalid-id/upvote', headers=headers)
        assert response.status_code == 400

    def test_upvote_shows_in_user_vote_field(self, client, other_user_token, thread_for_voting):
        """Test that upvote is reflected in user_vote field."""
        headers = {'Authorization': f'Bearer {other_user_token}'}

        # Upvote
        client.post(f'/api/threads/{thread_for_voting}/upvote', headers=headers)

        # Get thread
        response = client.get(f'/api/threads/{thread_for_voting}', headers=headers)
        assert response.status_code == 200
        assert response.json.get('user_vote') == 'upvote'


class TestThreadDownvote:
    """Tests for downvoting threads."""

    def test_downvote_thread_success(self, client, other_user_token, thread_for_voting):
        """Test successful downvote of a thread."""
        headers = {'Authorization': f'Bearer {other_user_token}'}
        response = client.post(f'/api/threads/{thread_for_voting}/downvote', headers=headers)

        assert response.status_code == 201
        assert 'score' in response.json
        assert response.json['score'] == -1

    def test_downvote_thread_decreases_score(self, client, other_user_token, thread_for_voting):
        """Test that downvoting decreases thread score."""
        headers = {'Authorization': f'Bearer {other_user_token}'}

        # Get initial thread
        get_response = client.get(f'/api/threads/{thread_for_voting}', headers=headers)
        initial_score = get_response.json.get('score', 0)

        # Downvote
        vote_response = client.post(f'/api/threads/{thread_for_voting}/downvote', headers=headers)
        assert vote_response.status_code == 201

        # Verify score decreased
        get_response = client.get(f'/api/threads/{thread_for_voting}', headers=headers)
        new_score = get_response.json['score']
        assert new_score == initial_score - 1

    def test_downvote_thread_toggle_removes_vote(self, client, other_user_token, thread_for_voting):
        """Test that downvoting twice toggles the vote (removes it)."""
        headers = {'Authorization': f'Bearer {other_user_token}'}

        # First downvote
        response1 = client.post(f'/api/threads/{thread_for_voting}/downvote', headers=headers)
        assert response1.status_code == 201
        assert response1.json['score'] == -1

        # Second downvote (toggle off)
        response2 = client.post(f'/api/threads/{thread_for_voting}/downvote', headers=headers)
        assert response2.status_code == 201
        assert response2.json['score'] == 0

    def test_downvote_thread_after_upvote_changes_vote(self, client, other_user_token, thread_for_voting):
        """Test that downvoting after upvote changes the vote."""
        headers = {'Authorization': f'Bearer {other_user_token}'}

        # Upvote first
        response1 = client.post(f'/api/threads/{thread_for_voting}/upvote', headers=headers)
        assert response1.status_code == 201
        assert response1.json['score'] == 1

        # Then downvote (should change from upvote to downvote)
        response2 = client.post(f'/api/threads/{thread_for_voting}/downvote', headers=headers)
        assert response2.status_code == 201
        assert response2.json['score'] == -1

    def test_downvote_thread_unauthorized(self, client, thread_for_voting):
        """Test downvoting without authentication."""
        response = client.post(f'/api/threads/{thread_for_voting}/downvote')
        assert response.status_code == 401

    def test_downvote_shows_in_user_vote_field(self, client, other_user_token, thread_for_voting):
        """Test that downvote is reflected in user_vote field."""
        headers = {'Authorization': f'Bearer {other_user_token}'}

        # Downvote
        client.post(f'/api/threads/{thread_for_voting}/downvote', headers=headers)

        # Get thread
        response = client.get(f'/api/threads/{thread_for_voting}', headers=headers)
        assert response.status_code == 200
        assert response.json.get('user_vote') == 'downvote'


class TestPostUpvote:
    """Tests for upvoting posts."""

    def test_upvote_post_success(self, client, other_user_token, post_for_voting):
        """Test successful upvote of a post."""
        headers = {'Authorization': f'Bearer {other_user_token}'}
        response = client.post(f'/api/posts/{post_for_voting}/upvote', headers=headers)

        assert response.status_code == 201
        assert 'score' in response.json
        assert response.json['score'] == 1

    def test_upvote_post_increases_score(self, client, other_user_token, post_for_voting):
        """Test that upvoting increases post score."""
        headers = {'Authorization': f'Bearer {other_user_token}'}

        # Get initial post
        get_response = client.get(f'/api/posts/{post_for_voting}', headers=headers)
        initial_score = get_response.json.get('score', 0)

        # Upvote
        vote_response = client.post(f'/api/posts/{post_for_voting}/upvote', headers=headers)
        assert vote_response.status_code == 201

        # Verify score increased
        get_response = client.get(f'/api/posts/{post_for_voting}', headers=headers)
        new_score = get_response.json['score']
        assert new_score == initial_score + 1

    def test_upvote_post_toggle_removes_vote(self, client, other_user_token, post_for_voting):
        """Test that upvoting twice toggles the vote (removes it)."""
        headers = {'Authorization': f'Bearer {other_user_token}'}

        # First upvote
        response1 = client.post(f'/api/posts/{post_for_voting}/upvote', headers=headers)
        assert response1.status_code == 201
        assert response1.json['score'] == 1

        # Second upvote (toggle off)
        response2 = client.post(f'/api/posts/{post_for_voting}/upvote', headers=headers)
        assert response2.status_code == 201
        assert response2.json['score'] == 0

    def test_upvote_post_after_downvote_changes_vote(self, client, other_user_token, post_for_voting):
        """Test that upvoting after downvote changes the vote."""
        headers = {'Authorization': f'Bearer {other_user_token}'}

        # Downvote first
        response1 = client.post(f'/api/posts/{post_for_voting}/downvote', headers=headers)
        assert response1.status_code == 201
        assert response1.json['score'] == -1

        # Then upvote (should change from downvote to upvote, +2 swing)
        response2 = client.post(f'/api/posts/{post_for_voting}/upvote', headers=headers)
        assert response2.status_code == 201
        assert response2.json['score'] == 1

    def test_upvote_post_unauthorized(self, client, post_for_voting):
        """Test upvoting without authentication."""
        response = client.post(f'/api/posts/{post_for_voting}/upvote')
        assert response.status_code == 401

    def test_upvote_non_existent_post(self, client, registered_user_token):
        """Test upvoting a non-existent post."""
        headers = {'Authorization': f'Bearer {registered_user_token}'}
        response = client.post('/api/posts/507f1f77bcf86cd799439011/upvote', headers=headers)
        assert response.status_code == 404

    def test_upvote_post_invalid_id(self, client, registered_user_token):
        """Test upvoting with invalid post ID."""
        headers = {'Authorization': f'Bearer {registered_user_token}'}
        response = client.post('/api/posts/invalid-id/upvote', headers=headers)
        assert response.status_code == 400


class TestPostDownvote:
    """Tests for downvoting posts."""

    def test_downvote_post_success(self, client, other_user_token, post_for_voting):
        """Test successful downvote of a post."""
        headers = {'Authorization': f'Bearer {other_user_token}'}
        response = client.post(f'/api/posts/{post_for_voting}/downvote', headers=headers)

        assert response.status_code == 201
        assert 'score' in response.json
        assert response.json['score'] == -1

    def test_downvote_post_decreases_score(self, client, other_user_token, post_for_voting):
        """Test that downvoting decreases post score."""
        headers = {'Authorization': f'Bearer {other_user_token}'}

        # Get initial post
        get_response = client.get(f'/api/posts/{post_for_voting}', headers=headers)
        initial_score = get_response.json.get('score', 0)

        # Downvote
        vote_response = client.post(f'/api/posts/{post_for_voting}/downvote', headers=headers)
        assert vote_response.status_code == 201

        # Verify score decreased
        get_response = client.get(f'/api/posts/{post_for_voting}', headers=headers)
        new_score = get_response.json['score']
        assert new_score == initial_score - 1

    def test_downvote_post_toggle_removes_vote(self, client, other_user_token, post_for_voting):
        """Test that downvoting twice toggles the vote (removes it)."""
        headers = {'Authorization': f'Bearer {other_user_token}'}

        # First downvote
        response1 = client.post(f'/api/posts/{post_for_voting}/downvote', headers=headers)
        assert response1.status_code == 201
        assert response1.json['score'] == -1

        # Second downvote (toggle off)
        response2 = client.post(f'/api/posts/{post_for_voting}/downvote', headers=headers)
        assert response2.status_code == 201
        assert response2.json['score'] == 0

    def test_downvote_post_after_upvote_changes_vote(self, client, other_user_token, post_for_voting):
        """Test that downvoting after upvote changes the vote."""
        headers = {'Authorization': f'Bearer {other_user_token}'}

        # Upvote first
        response1 = client.post(f'/api/posts/{post_for_voting}/upvote', headers=headers)
        assert response1.status_code == 201
        assert response1.json['score'] == 1

        # Then downvote (should change from upvote to downvote, -2 swing)
        response2 = client.post(f'/api/posts/{post_for_voting}/downvote', headers=headers)
        assert response2.status_code == 201
        assert response2.json['score'] == -1

    def test_downvote_post_unauthorized(self, client, post_for_voting):
        """Test downvoting without authentication."""
        response = client.post(f'/api/posts/{post_for_voting}/downvote')
        assert response.status_code == 401


class TestVotingScenarios:
    """Complex voting scenarios."""

    def test_multiple_users_voting(self, client, registered_user_token, other_user_token, thread_for_voting):
        """Test multiple users voting on the same thread."""
        headers1 = {'Authorization': f'Bearer {registered_user_token}'}
        headers2 = {'Authorization': f'Bearer {other_user_token}'}

        # User 1 upvotes
        response1 = client.post(f'/api/threads/{thread_for_voting}/upvote', headers=headers1)
        assert response1.status_code == 201
        assert response1.json['score'] == 1

        # User 2 also upvotes
        response2 = client.post(f'/api/threads/{thread_for_voting}/upvote', headers=headers2)
        assert response2.status_code == 201
        assert response2.json['score'] == 2

        # User 1 changes to downvote
        response3 = client.post(f'/api/threads/{thread_for_voting}/downvote', headers=headers1)
        assert response3.status_code == 201
        assert response3.json['score'] == 0  # +1 from user2, -1 from user1

    def test_vote_sequence_upvote_downvote_remove(self, client, other_user_token, thread_for_voting):
        """Test complex voting sequence."""
        headers = {'Authorization': f'Bearer {other_user_token}'}

        # Upvote
        r1 = client.post(f'/api/threads/{thread_for_voting}/upvote', headers=headers)
        assert r1.json['score'] == 1

        # Change to downvote
        r2 = client.post(f'/api/threads/{thread_for_voting}/downvote', headers=headers)
        assert r2.json['score'] == -1

        # Remove downvote
        r3 = client.post(f'/api/threads/{thread_for_voting}/downvote', headers=headers)
        assert r3.json['score'] == 0

        # Upvote again
        r4 = client.post(f'/api/threads/{thread_for_voting}/upvote', headers=headers)
        assert r4.json['score'] == 1

    def test_voting_persists_across_requests(self, client, other_user_token, thread_for_voting):
        """Test that votes persist across different requests."""
        headers = {'Authorization': f'Bearer {other_user_token}'}

        # Upvote
        client.post(f'/api/threads/{thread_for_voting}/upvote', headers=headers)

        # Get thread in new request
        response1 = client.get(f'/api/threads/{thread_for_voting}', headers=headers)
        assert response1.json['score'] == 1
        assert response1.json['user_vote'] == 'upvote'

        # Get thread again
        response2 = client.get(f'/api/threads/{thread_for_voting}', headers=headers)
        assert response2.json['score'] == 1
        assert response2.json['user_vote'] == 'upvote'

    def test_thread_list_shows_correct_vote_status(self, client, other_user_token, thread_for_voting):
        """Test that thread list shows correct user_vote status."""
        headers = {'Authorization': f'Bearer {other_user_token}'}

        # Upvote thread
        client.post(f'/api/threads/{thread_for_voting}/upvote', headers=headers)

        # List threads
        response = client.get('/api/threads', headers=headers)
        assert response.status_code == 200

        # Find the thread in the list
        thread = next((t for t in response.json['threads'] if t['id'] == thread_for_voting), None)
        assert thread is not None
        assert thread['user_vote'] == 'upvote'

    def test_different_users_see_different_vote_status(self, client, registered_user_token, other_user_token, thread_for_voting):
        """Test that different users see their own vote status."""
        headers1 = {'Authorization': f'Bearer {registered_user_token}'}
        headers2 = {'Authorization': f'Bearer {other_user_token}'}

        # User 1 upvotes
        client.post(f'/api/threads/{thread_for_voting}/upvote', headers=headers1)

        # User 2 downvotes
        client.post(f'/api/threads/{thread_for_voting}/downvote', headers=headers2)

        # User 1 sees their upvote
        response1 = client.get(f'/api/threads/{thread_for_voting}', headers=headers1)
        assert response1.json['user_vote'] == 'upvote'

        # User 2 sees their downvote
        response2 = client.get(f'/api/threads/{thread_for_voting}', headers=headers2)
        assert response2.json['user_vote'] == 'downvote'

        # Score is 0 (one upvote, one downvote)
        assert response1.json['score'] == 0
        assert response2.json['score'] == 0


class TestVotingEdgeCases:
    """Edge cases for voting."""

    def test_vote_on_deleted_content_should_fail(self, client, registered_user_token, other_user_token, thread_data):
        """Test voting on deleted content."""
        headers1 = {'Authorization': f'Bearer {registered_user_token}'}
        headers2 = {'Authorization': f'Bearer {other_user_token}'}

        # Create thread
        response = client.post('/api/threads', json=thread_data, headers=headers1)
        thread_id = response.json['id']

        # Delete thread
        client.delete(f'/api/threads/{thread_id}', headers=headers1)

        # Try to vote on deleted thread
        vote_response = client.post(f'/api/threads/{thread_id}/upvote', headers=headers2)
        assert vote_response.status_code == 404
