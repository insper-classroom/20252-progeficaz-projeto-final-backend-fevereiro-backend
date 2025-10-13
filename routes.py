from flask import Blueprint, request, jsonify, current_app
from models import Thread, Post
from mongoengine.errors import DoesNotExist, ValidationError
from bson import ObjectId

api_bp = Blueprint('api', __name__)


@api_bp.route('/threads', methods=['GET'])
def list_threads():
    threads = Thread.objects.order_by('-created_at')
    return jsonify([t.to_dict() for t in threads])


@api_bp.route('/threads', methods=['POST'])
def create_thread():
    data = request.get_json() or {}
    title = data.get('title')
    description = data.get('description')  # Optional description field
    if not title:
        return jsonify({'error': 'title required'}), 400
    
    try:
        thread = Thread(title=title, description=description)
        thread.save()
        return jsonify(thread.to_dict()), 201
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400


@api_bp.route('/threads/<thread_id>', methods=['GET'])
def get_thread(thread_id):
    try:
        thread = Thread.objects.get(id=thread_id)
        posts = Post.objects(thread=thread).order_by('created_at')
        data = thread.to_dict()
        data['posts'] = [p.to_dict() for p in posts]
        return jsonify(data)
    except DoesNotExist:
        return jsonify({'error': 'Thread not found'}), 404
    except Exception as e:
        return jsonify({'error': 'Invalid thread ID'}), 400


@api_bp.route('/threads/<thread_id>', methods=['PUT'])
def update_thread(thread_id):
    """Update a thread's title or description"""
    try:
        thread = Thread.objects.get(id=thread_id)
        data = request.get_json() or {}
        
        # Update fields if provided
        if 'title' in data:
            if not data['title']:
                return jsonify({'error': 'title cannot be empty'}), 400
            thread.title = data['title']
        if 'description' in data:
            thread.description = data['description']
        
        thread.save()
        return jsonify(thread.to_dict())
    except DoesNotExist:
        return jsonify({'error': 'Thread not found'}), 404
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Invalid thread ID'}), 400


@api_bp.route('/threads/<thread_id>/posts', methods=['POST'])
def create_post(thread_id):
    try:
        thread = Thread.objects.get(id=thread_id)
        data = request.get_json() or {}
        author = data.get('author') or 'Anonymous'
        content = data.get('content')
        if not content:
            return jsonify({'error': 'content required'}), 400
        
        post = Post(thread=thread, author=author, content=content)
        post.save()
        return jsonify(post.to_dict()), 201
    except DoesNotExist:
        return jsonify({'error': 'Thread not found'}), 404
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Invalid thread ID'}), 400


@api_bp.route('/posts/<post_id>', methods=['PUT'])
def update_post(post_id):
    """Update a post's content or author"""
    try:
        post = Post.objects.get(id=post_id)
        data = request.get_json() or {}
        
        # Update fields if provided
        if 'content' in data:
            post.content = data['content']
        if 'author' in data:
            post.author = data['author']
        
        post.save()
        return jsonify(post.to_dict())
    except DoesNotExist:
        return jsonify({'error': 'Post not found'}), 404
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Invalid post ID'}), 400


@api_bp.route('/posts/<post_id>', methods=['GET'])
def get_post(post_id):
    """Get a specific post by ID"""
    try:
        post = Post.objects.get(id=post_id)
        return jsonify(post.to_dict())
    except DoesNotExist:
        return jsonify({'error': 'Post not found'}), 404
    except Exception as e:
        return jsonify({'error': 'Invalid post ID'}), 400
