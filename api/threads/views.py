from flask import request, jsonify
from api.threads.models import Thread, Post
from api.authentication.models import User
from mongoengine.errors import DoesNotExist, ValidationError
from core.types import api_response
from core.utils import success_response, error_response, validation_error_response
from typing import Literal
from bson import ObjectId
from core.moderation import verificar_thread, verificar_post

# THREADS views
def list_threads(current_user: str) -> api_response:
    """List all threads with optional filters"""
    try:
        from flask import request
        
        # Get filter parameters
        semester = request.args.get('semester', type=int)
        courses = request.args.getlist('courses')
        subjects = request.args.getlist('subjects')
        
        # Build query
        filters = {}
        
        if semester:
            filters['semester'] = semester
        
        if courses:
            filters['courses__in'] = courses
        
        if subjects:
            filters['subjects__in'] = subjects
        
        # Apply filters
        if filters:
            threads = Thread.objects(**filters)
        else:
            threads = Thread.objects()
       
        data = {'threads': [tr.to_dict(user_id=current_user) for tr in threads]}
        
        return success_response(data=data, status_code=200)
    
    except Exception as e:
        import traceback
        print(f"Error in list_threads: {e}")
        traceback.print_exc()
        return error_response(f"Failed to retrieve threads: {str(e)}", 500)

def get_thread_by_id(thread_id: str, current_user: str) -> api_response:
    """Get a specific thread by ID along with its posts"""
    try:
        thread = Thread.objects.get(id=thread_id)
        posts = Post.objects(_thread=thread)
        data = thread.to_dict(user_id=current_user)
        data['posts'] = [p.to_dict(user_id=current_user) for p in posts]
        return success_response(data=data, status_code=200)
    except DoesNotExist:
        return error_response('Thread not found', 404)
    except Exception as e:
        return error_response('Invalid thread ID', 400)

def create_thread(data: dict, current_user: str) -> api_response:
    """Create a new thread"""
    title = data.get('title', '').strip()
    description = data.get('description', '').strip() # Optional description field
    
    # Filter fields (with defaults for backward compatibility)
    semester = data.get('semester', 1) # Default to 1st semester
    courses = data.get('courses', [])   # Default to empty list
    subjects = data.get('subjects', ['Geral'])  # Default subject
    
    # Validation
    
    # Handle both "2024.1" and integer formats
    semester = int(str(semester).split('.')[-1])

    if not title:
        return error_response('Title is required', 400)
    elif len(title) > 200:
        return error_response('Title must be less than 200 characters', 400)

    if description and len(description) > 500:
        return error_response('Description must be less than 500 characters', 400)
    
    try:
        if not (1 <= semester <= 10):
            return error_response(f'Semester must be between 1 and 10', 400)
    except (ValueError, IndexError):
        return error_response('Semester must be a valid number', 400)

    # Verificar moderação de conteúdo
    is_safe, moderation_message = verificar_thread(title, description)
    if not is_safe:
        return error_response(moderation_message, 400)
    
    try:
        thread = Thread(
            _author=ObjectId(current_user),
            _title=title, 
            _description=description,
            semester=semester,
            courses=courses,
            subjects=subjects
        )
        thread.save()
        return success_response(data=thread.to_dict(user_id=current_user), message="Thread created successfully", status_code=201)
    except ValidationError as e:
        return error_response(str(e), 400)
    except Exception as e:
        return error_response("Failed to create thread: " + str(e), 500)

def update_thread_by_id(thread_id: str, data: dict, current_user: str) -> api_response:
    """Update a thread's title or description"""
    try:
        thread = Thread.objects.get(id=thread_id, _author=ObjectId(current_user))

        # Verificar moderação dos campos que serão atualizados
        title_to_check = data.get('title', '').strip() if 'title' in data else None
        description_to_check = data.get('description', '').strip() if 'description' in data else None
        
        if title_to_check or description_to_check:
            is_safe, moderation_message = verificar_thread(
                title_to_check or thread._title,
                description_to_check if 'description' in data else thread._description
            )
            if not is_safe:
                return error_response(moderation_message, 400)
        
        # Update fields if provided
        
        thread.update(data)
        
        return success_response(message="Thread updated successfully", status_code=201)
    except DoesNotExist:
        return error_response('Thread not found', 404)
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Invalid thread ID: ' + str(e)}), 400


def delete_thread_by_id(thread_id: str, current_user: str) -> api_response:
    """Delete a thread and all its associated posts"""
    try:
        thread = Thread.objects.get(id=thread_id)
        
        if str(thread.author.id) != current_user:
            return error_response('Only the thread owner can delete the thread', 403)
        
        # Delete associated posts
        Post.objects(_thread=thread)
        for post in Post.objects(_thread=thread):
            post.delete()
        thread.delete()

        return success_response(message='Thread and associated posts deleted successfully', status_code=200)
    except DoesNotExist:
        return error_response('Thread not found', 404)
    except Exception as e:
        return error_response('Invalid thread ID', 400)


# POSTS views 

def get_post_by_id(post_id: str, current_user: str) -> api_response:
    """Get a specific post by ID"""
    try:
        post = Post.objects.get(id=post_id)
        return success_response(data=post.to_dict(user_id=current_user), status_code=200)
    except DoesNotExist:
        return error_response('Post not found', 404)
    except Exception as e:
        return error_response('Invalid post ID', 400)

def create_post(thread_id: str, data: dict, current_user: str) -> api_response:
    """Create a new post in a thread"""
    try:
        content = data.get('content')
        if not content:
            return error_response('Content is required', 400)

        # Verificar moderação do conteúdo
        is_safe, moderation_message = verificar_post(content)
        if not is_safe:
            return error_response(moderation_message, 400)

        post = Post(_thread=ObjectId(thread_id), _author=ObjectId(current_user), _content=content)
        post.save()
        return success_response(data=post.to_dict(user_id=current_user), message="Post created successfully", status_code=201)
    except DoesNotExist:
        return error_response('Thread not found', 404)
    except ValidationError as e:
        return error_response("Invalid thread ID", 400)
    except Exception as e:
        return error_response('Invalid thread ID', 400)

def update_post_by_id(post_id: str, data: dict, current_user: str) -> api_response:
    """Update a post's content or author"""
    try:
        post = Post.objects.get(id=post_id)
        if str(post.author.id) != current_user:
            return error_response('You do not have permission to update this post', 403)

        # Verificar moderação do conteúdo se estiver sendo atualizado
        if 'content' in data:
            content_to_check = data.get('content', '').strip()
            if content_to_check:
                is_safe, moderation_message = verificar_post(content_to_check)
                if not is_safe:
                    return error_response(moderation_message, 400)
        
        post.update_content(data['content'])

        return success_response(message="Post updated successfully", status_code=201)
    except DoesNotExist:
        return error_response('Post not found', 404)
    except Exception as e:
        return error_response('Invalid post ID', 400)


def delete_post_by_id(post_id: str, current_user: str) -> api_response:
    """Delete a specific post"""
    try:
        post = Post.objects.get(id=post_id)
        if str(post.author.id) != current_user:
            return error_response('You do not have permission to delete this post', 403)
        post.delete()
        return success_response(message='Post deleted successfully', status_code=200)
    except DoesNotExist:
        return error_response('Post not found', 404)
    except Exception as e:
        return error_response('Invalid post ID', 400)


# VOTING views


def upvote_by_id(obj_id: str, current_user: str, obj_type: Literal["threads","posts"]) -> api_response:
    """Upvote a specific post (one vote per user)"""
    try:
        if obj_type == "posts":
            obj = Post.objects.get(id=obj_id)
        elif obj_type == "threads":
            obj = Thread.objects.get(id=obj_id)
        else:
            return error_response('Object not found', 404)
        
        # Upvote logic
        obj.upvote(current_user)

        return success_response(
            data={'score': obj.score},
            message =f'{obj_type} upvoted successfully',
            status_code=201
        )
    except DoesNotExist:
        return error_response(f'{obj_type} not found', 404)
    except Exception as e:
        return error_response('Invalid obj ID or voting failed', 400)



def downvote_by_id(obj_id: str, current_user: str, obj_type: Literal["thread","post"]) -> api_response:
    """Downvote a specific post (one vote per user)"""
    try:
        if obj_type == "posts":
            obj = Post.objects.get(id=obj_id)
        elif obj_type == "threads":
            obj = Thread.objects.get(id=obj_id)
        else:
            return error_response('Object not found', 404)

        # Donwvote logic
        obj.downvote(current_user)
        
        return success_response(
            data={'score': obj.score},
            message=f'{obj_type} downvoted successfully',
            status_code=201
        )
    except DoesNotExist:
        return error_response(f'{obj_type} not found', 404)
    except Exception as e:
        return error_response('Invalid obj ID or voting failed', 400)





# POST PIN views

def pin_post_by_id(post_id: str, current_user: str) -> api_response:
    """Pin a post (only thread owner can pin posts)"""
    try:
        post = Post.objects.get(id=post_id)
        thread = post.thread
        
        # Check if current user is the thread owner
        if str(thread.author.id) != current_user:
            return error_response('Only the thread owner can pin posts', 403)
        
        # Pin the post
        post.pin()
        
        return success_response(
            data={'pinned': post.pinned},
            message='Post pinned successfully',
            status_code=200
        )
    except DoesNotExist:
        return error_response('Post not found', 404)
    except Exception as e:
        return error_response('Invalid post ID or pin failed: ' + str(e), 400)

def unpin_post_by_id(post_id: str, current_user: str) -> api_response:
    """Unpin a post (only thread owner can unpin posts)"""
    try:
        post = Post.objects.get(id=post_id)
        thread = post.get_thread()
        
        # Check if current user is the thread owner
        if str(thread.author.id) != current_user:
            return error_response('Only the thread owner can unpin posts', 403)
        
        # Unpin the post
        post.unpin()
        
        return success_response(
            data={'pinned': post.pinned},
            message='Post unpinned successfully',
            status_code=200
        )
    except DoesNotExist:
        return error_response('Post not found', 404)
    except Exception as e:
        return error_response('Invalid post ID or unpin failed', 400)
