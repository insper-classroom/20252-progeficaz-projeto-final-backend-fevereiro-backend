from flask import request, jsonify
from api.threads.models import Thread, Post
from mongoengine.errors import DoesNotExist, ValidationError
from core.types import api_response
from core.utils import success_response, error_response, validation_error_response

# THREADS views
def list_threads() -> api_response:
    """List all threads"""
    try:

        # Build query
        query = Thread.objects
        # Apply ordering
        threads = query.order_by('-created_at')
        
        # Prepare response
        data = {
            'threads': [t.to_dict() for t in threads]
        }
        
        return success_response(data=data, status_code=200)
    
    except Exception as e:
        return error_response("Failed to retrieve threads", 500)

def get_thread_by_id(thread_id: str) -> api_response:
    """Get a specific thread by ID along with its posts"""
    try:
        thread = Thread.objects.get(id=thread_id)
        posts = Post.objects(thread=thread).order_by('created_at')
        data = thread.to_dict()
        data['posts'] = [p.to_dict() for p in posts]
        return success_response(data=data, status_code=200)
    except DoesNotExist:
        return error_response('Thread not found', 404)
    except Exception as e:
        return error_response('Invalid thread ID', 400)

def create_thread(data: dict) -> api_response:
    """Create a new thread"""
    
    title = data.get('title', '').strip()
    description = data.get('description', '').strip() # Optional description field
    
    # Filter fields (with defaults for backward compatibility)
    semester = data.get('semester', 1) # Default to 1st semester
    courses = data.get('courses', [])   # Default to empty list
    subjects = data.get('subjects', ['Geral'])  # Default subject
    
    # Validation
    errors = {}
    if not title:
        errors['title'] = 'Title is required'
    elif len(title) > 200:
        errors['title'] = 'Title must be less than 200 characters'
    
    if description and len(description) > 500:
        errors['description'] = 'Description must be less than 500 characters'
    
    if semester < 1 or semester > 10:
        errors['semester'] = 'Semester must be between 1 and 10'
    
    if errors:
        return validation_error_response(errors)
    
    try:
        thread = Thread(
            title=title, 
            description=description,
            semester=semester,
            courses=courses,
            subjects=subjects
        )
        thread.save()
        return success_response(data=thread.to_dict(), message="Thread created successfully", status_code=201)
    except ValidationError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response("Failed to create thread", 500)

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
        return success_response(message="Thread updated successfully", status_code=201)
    except DoesNotExist:
        return error_response('Thread not found', 404)
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Invalid thread ID'}), 400


def delete_thread_by_id(thread_id: str) -> api_response:
    """Delete a thread and all its associated posts"""
    try:
        thread = Thread.objects.get(id=thread_id)
        
        # Delete all posts associated with this thread
        Post.objects(thread=thread).delete()
        
        # Delete the thread
        thread.delete()
        
        return success_response(message='Thread and associated posts deleted successfully', status_code=200)
    except DoesNotExist:
        return error_response('Thread not found', 404)
    except Exception as e:
        return error_response('Invalid thread ID', 400)


# POSTS views 

def get_post_by_id(post_id: str) -> api_response:
    """Get a specific post by ID"""
    try:
        post = Post.objects.get(id=post_id)
        return success_response(data=post.to_dict(), status_code=200)
    except DoesNotExist:
        return error_response('Post not found', 404)
    except Exception as e:
        return error_response('Invalid post ID', 400)

def create_post(thread_id: str, data: dict) -> api_response:
    """Create a new post in a thread"""
    try:
        thread = Thread.objects.get(id=thread_id)
        author = data.get('author') or 'Anonymous'
        content = data.get('content')
        if not content:
            return error_response('content required', 400)
        
        post = Post(thread=thread, author=author, content=content)
        post.save()
        return success_response(data=post.to_dict(), message="Post created successfully", status_code=201)
    except DoesNotExist:
        return error_response('Thread not found', 404)
    except ValidationError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response('Invalid thread ID', 400)

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
        return success_response( message="Post updated successfully", status_code=201)
    except DoesNotExist:
        return error_response('Post not found', 404)
    except ValidationError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response('Invalid thread ID', 400)


def delete_post_by_id(post_id: str) -> api_response:
    """Delete a specific post"""
    try:
        post = Post.objects.get(id=post_id)
        post.delete()
        return success_response(message='Post deleted successfully', status_code=200)
    except DoesNotExist:
        return error_response('Post not found', 404)
    except Exception as e:
        return error_response('Invalid post ID', 400)
