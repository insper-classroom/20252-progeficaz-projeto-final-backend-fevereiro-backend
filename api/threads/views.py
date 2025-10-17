from flask import request, jsonify
from api.threads.models import Thread, Post
from mongoengine.errors import DoesNotExist, ValidationError
from core.types import api_response

# THREADS views
def list_threads() -> api_response:
    """List all threads"""
    threads = Thread.objects.order_by('-created_at')
    return jsonify([t.to_dict() for t in threads]), 200

def get_thread_by_id(thread_id: str) -> api_response:
    """Get a specific thread by ID along with its posts"""
    try:
        thread = Thread.objects.get(id=thread_id)
        posts = Post.objects(thread=thread).order_by('created_at')
        data = thread.to_dict()
        data['posts'] = [p.to_dict() for p in posts]
        return jsonify(data), 200
    except DoesNotExist:
        return jsonify({'error': 'Thread not found'}), 404
    except Exception as e:
        return jsonify({'error': 'Invalid thread ID'}), 400

def create_thread(data: dict) -> api_response:
    """Create a new thread"""
    
    title = data.get('title')
    description = data.get('description')  # Optional description field
    
    # Filter fields (with defaults for backward compatibility)
    semester = data.get('semester', 1)  # Default to 1st semester
    courses = data.get('courses', [])   # Default to empty list
    subjects = data.get('subjects', ['Geral'])  # Default subject
    
    if not title:
        return jsonify({'error': 'title required'}), 400
    
    try:
        thread = Thread(
            title=title, 
            description=description,
            semester=semester,
            courses=courses,
            subjects=subjects
        )
        thread.save()
        return jsonify(thread.to_dict()), 201
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400

def update_thread_by_id(thread_id: str, data: dict) -> api_response:
    """Update a thread's title or description"""
    try:
        thread = Thread.objects.get(id=thread_id)
        
        # Update fields if provided
        if 'title' in data:
            if not data['title']:
                return jsonify({'error': 'title cannot be empty'}), 400
            thread.title = data['title']
        if 'description' in data:
            thread.description = data['description']
        if 'semester' in data:
            thread.semester = data['semester']
        if 'courses' in data:
            thread.courses = data['courses']
        if 'subjects' in data:
            thread.subjects = data['subjects']
        
        thread.save()
        return jsonify(thread.to_dict()), 200
    except DoesNotExist:
        return jsonify({'error': 'Thread not found'}), 404
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Invalid thread ID'}), 400


# POSTS views 

def get_post_by_id(post_id: str) -> api_response:
    """Get a specific post by ID"""
    try:
        post = Post.objects.get(id=post_id)
        return jsonify(post.to_dict()), 200
    except DoesNotExist:
        return jsonify({'error': 'Post not found'}), 404
    except Exception as e:
        return jsonify({'error': 'Invalid post ID'}), 400

def create_post(thread_id: str, data: dict) -> api_response:
    """Create a new post in a thread"""
    try:
        thread = Thread.objects.get(id=thread_id)
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

def update_post_by_id(post_id: str, data: dict) -> api_response:
    """Update a post's content or author"""
    try:
        post = Post.objects.get(id=post_id)
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