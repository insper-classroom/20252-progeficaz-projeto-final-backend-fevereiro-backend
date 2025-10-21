from flask import Blueprint, request
from api.threads import views as vi

threads_bp = Blueprint('threads', __name__)


# THREADS endpoints

@threads_bp.route('/threads', methods=['GET'])
def list_threads():
    """List all threads"""
    return vi.list_threads()

@threads_bp.route('/threads', methods=['POST'])
def create_thread():
    """Create a new thread"""
    data = request.get_json() or {}
    return vi.create_thread(data)

@threads_bp.route('/threads/<thread_id>', methods=['GET'])
def get_thread(thread_id):
    """Get a specific thread by ID"""
    return vi.get_thread_by_id(thread_id)

@threads_bp.route('/threads/<thread_id>', methods=['PUT'])
def update_thread(thread_id):
    """Update a thread's title, description, or filters"""
    data = request.get_json() or {}
    return vi.update_thread_by_id(thread_id, data)

@threads_bp.route('/threads/<thread_id>', methods=['DELETE'])
def delete_thread(thread_id):
    """Delete a thread and all its posts"""
    return vi.delete_thread_by_id(thread_id)


# POSTS endpoints

@threads_bp.route('/posts/<post_id>', methods=['GET'])
def get_post(post_id):
    """Get a specific post by ID"""
    return vi.get_post_by_id(post_id)

@threads_bp.route('/threads/<thread_id>/posts', methods=['POST'])
def create_post(thread_id):
    """Create a new post in a thread"""
    data = request.get_json() or {}
    return vi.create_post(thread_id, data)

@threads_bp.route('/posts/<post_id>', methods=['PUT'])
def update_post(post_id):
    """Update a post's content or author"""
    data = request.get_json() or {}
    return vi.update_post_by_id(post_id, data)

@threads_bp.route('/posts/<post_id>', methods=['DELETE'])
def delete_post(post_id):
    """Delete a specific post"""
    return vi.delete_post_by_id(post_id)


# VOTING endpoints

@threads_bp.route('/posts/<post_id>/upvote', methods=['POST'])
def upvote_post(post_id):
    """Upvote a specific post"""
    return vi.upvote_post_by_id(post_id)

@threads_bp.route('/posts/<post_id>/downvote', methods=['POST'])
def downvote_post(post_id):
    """Downvote a specific post"""
    return vi.downvote_post_by_id(post_id)

@threads_bp.route('/posts/<post_id>/vote', methods=['DELETE'])
def remove_vote(post_id):
    """Remove user's vote from a specific post"""
    return vi.remove_vote_by_post_id(post_id)


# THREAD VOTING endpoints

@threads_bp.route('/threads/<thread_id>/upvote', methods=['POST'])
def upvote_thread(thread_id):
    """Upvote a specific thread"""
    return vi.upvote_thread_by_id(thread_id)

@threads_bp.route('/threads/<thread_id>/downvote', methods=['POST'])
def downvote_thread(thread_id):
    """Downvote a specific thread"""
    return vi.downvote_thread_by_id(thread_id)

@threads_bp.route('/threads/<thread_id>/vote', methods=['DELETE'])
def remove_thread_vote(thread_id):
    """Remove user's vote from a specific thread"""
    return vi.remove_thread_vote_by_id(thread_id)