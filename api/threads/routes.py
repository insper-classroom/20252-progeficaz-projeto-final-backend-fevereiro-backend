from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from api.threads import views as vi
from typing import Literal

threads_bp = Blueprint("threads", __name__)


# THREADS endpoints


@threads_bp.route("/threads", methods=["GET"])
@jwt_required()
def list_threads():
    """List all threads"""
    return vi.list_threads()


@threads_bp.route("/threads", methods=["POST"])
@jwt_required()
def create_thread():
    """Create a new thread"""
    data = request.get_json() or {}
    current_user = get_jwt_identity()
    return vi.create_thread(data, current_user)


@threads_bp.route("/threads/<thread_id>", methods=["GET"])
@jwt_required()
def get_thread(thread_id):
    """Get a specific thread by ID"""
    return vi.get_thread_by_id(thread_id)


@threads_bp.route("/threads/<thread_id>", methods=["PUT"])
@jwt_required()
def update_thread(thread_id):
    """Update a thread's title, description, or filters"""
    data = request.get_json() or {}
    current_user = get_jwt_identity()
    return vi.update_thread_by_id(thread_id, data, current_user)


@threads_bp.route("/threads/<thread_id>", methods=["DELETE"])
@jwt_required()
def delete_thread(thread_id):
    """Delete a thread and all its posts"""
    current_user = get_jwt_identity()
    return vi.delete_thread_by_id(thread_id, current_user)


# POSTS endpoints


@threads_bp.route("/posts/<post_id>", methods=["GET"])
@jwt_required()
def get_post(post_id):
    """Get a specific post by ID"""
    return vi.get_post_by_id(post_id)


@threads_bp.route("/threads/<thread_id>/posts", methods=["POST"])
@jwt_required()
def create_post(thread_id):
    """Create a new post in a thread"""
    data = request.get_json() or {}
    current_user = get_jwt_identity()
    return vi.create_post(thread_id, data, current_user)


@threads_bp.route("/posts/<post_id>", methods=["PUT"])
@jwt_required()
def update_post(post_id):
    """Update a post's content or author"""
    data = request.get_json() or {}
    current_user = get_jwt_identity()
    return vi.update_post_by_id(post_id, data, current_user)


@threads_bp.route("/posts/<post_id>", methods=["DELETE"])
@jwt_required()
def delete_post(post_id):
    """Delete a specific post"""
    current_user = get_jwt_identity()
    return vi.delete_post_by_id(post_id, current_user)


# VOTING endpoints


@threads_bp.route("/<obj_type>/<post_id>/upvote", methods=["POST"])
@jwt_required()
def upvote_post(obj_type: Literal["threads", "posts"], post_id: str):
    """Upvote a specific post or thread"""
    current_user = get_jwt_identity()
    return vi.upvote_by_id(post_id, current_user,obj_type)


@threads_bp.route("/<obj_type>/<post_id>/downvote", methods=["POST"])
@jwt_required()
def downvote_post(obj_type: Literal["threads", "posts"], post_id: str):
    """Downvote a specific post or thread"""
    current_user = get_jwt_identity()
    return vi.downvote_by_id(post_id, current_user,obj_type)


# POST PIN endpoints

@threads_bp.route('/posts/<post_id>/pin', methods=['POST'])
@jwt_required()
def pin_post(post_id):
    """Pin a post (only thread owner can pin posts)"""
    current_user = get_jwt_identity()
    return vi.pin_post_by_id(post_id, current_user)

@threads_bp.route('/posts/<post_id>/pin', methods=['DELETE'])
@jwt_required()
def unpin_post(post_id):
    """Unpin a post (only thread owner can unpin posts)"""
    current_user = get_jwt_identity()
    return vi.unpin_post_by_id(post_id, current_user)
