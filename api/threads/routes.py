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