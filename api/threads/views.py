from flask import request, jsonify, Response
from api.threads.models import Thread, Post, ThreadImage
from api.authentication.models import User
from mongoengine.errors import DoesNotExist, ValidationError
from core.types import api_response
from core.utils import success_response, error_response, allowed_filename
from werkzeug.utils import secure_filename
from typing import Literal
from bson import ObjectId
from core.moderation import verificar_thread, verificar_post
from gridfs import GridFS
from bson.objectid import ObjectId
from core.constants import MAX_AVATAR_BYTES

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
    
# THREAD IMAGE views

def upload_thread_images(thread_id, current_user, files) -> api_response:
    """
    multipart/form-data with file field "image"
    """
    if not files or len(files) == 0:
        return error_response("No file provided", 400)

    thread = Thread.objects(id=ObjectId(thread_id)).first()
    if not thread:
        return error_response("Thread not found", 404)

    if str(thread.author.id) != current_user:
        return error_response("You do not have permission to upload images to this thread", 403)

    erros = []
    for file in files:
        filename = file.filename or ""
        if not allowed_filename(filename):
            erros.append("Unsupported file type. Allowed: png, jpg, jpeg, gif, webp")
            continue

        # Protect against huge uploads (we check size by peeking into stream)
        file.stream.seek(0, 2)  # seek to end
        size = file.stream.tell()
        file.stream.seek(0)     # rewind

        if size > MAX_AVATAR_BYTES:
            erros.append("File too large (max 5 MB)")
            continue

        result = thread.attach_image(file.stream, secure_filename(file.filename), file.mimetype)
        if "error" in result:
            erros.append(result["error"])
    if erros:
        return error_response("Image upload errors occurred: " + ", ".join(erros), 400)
        
    return success_response(message="Images uploaded successfully", data={"thread_id": str(thread.id)})


def get_thread_image(image_id: str, current_user: str) -> api_response:
    """
    Streams all images stored in GridFS for a post
    """
    try:
        image = ThreadImage.objects(id=ObjectId(image_id)).first()
        if not image:
            return error_response("Image not found", 404)

        # Check if current user is authorized to view the image
        thread = image.thread
        if str(thread.author.id) != current_user:
            return error_response("You do not have permission to view this image", 403)

        return Response(image.image.read(), mimetype=image.image.content_type)
    except Exception as e:
        return error_response("Failed to retrieve image", 500)
    except Exception as e:
        pass
    
def list_thread_images(thread_id: str, current_user: str) -> api_response:
    """Get all images uploaded to a specific thread"""
    thread = Thread.objects(id=ObjectId(thread_id)).first()
    if not thread:
        return error_response("Thread not found", 404)

    images = ThreadImage.objects(thread=thread)
    image_list = []
    for img in images:
        image_list.append({
            "id": str(img.id),
            "filename": getattr(img.image, "filename", ""),
            "content_type": getattr(img.image, "content_type", ""),
        })

    return success_response(data={"images": image_list}, status_code=200)

def delete_thread_image(image_id: str, current_user: str) -> api_response:
    """Delete a specific image from a thread"""
    try:
        image = ThreadImage.objects(id=ObjectId(image_id)).first()
        if not image:
            return error_response("Image not found", 404)

        thread = image.thread
        if str(thread.author.id) != current_user:
            return error_response("You do not have permission to delete this image", 403)

        image.delete()
        return success_response(message="Image deleted successfully", status_code=200)
    except Exception as e:
        return error_response("Failed to delete image", 500)
    
# USER views

def get_user_avatar(user_id: str, current_user: str) -> api_response:
    """
    GET /api/users/<user_id>/avatar
    returns the avatar image binary with correct content-type
    """
    user = User.objects(id=ObjectId(user_id)).first()
    if not user:
        return error_response("User not found", 404)

    avatar = user.get_avatar()
    if not avatar:
        return error_response("No avatar set", 404)

    try:
        data = avatar.read()
        content_type = getattr(avatar, "content_type", "application/octet-stream")
        return Response(data, mimetype=content_type)
    except Exception:
        return error_response("Failed to read avatar", 500)
    
def upload_avatar(current_user, files):
    """
    POST /api/users/avatar
    multipart/form-data with file field "avatar"
    """
    if not files:
        return error_response("No file provided", 400)
    
    if len(files) > 1:
        return error_response("Only one avatar file can be uploaded", 400)

    file = files[0]

    filename = file.filename or ""
    if not allowed_filename(filename):
        return error_response("Unsupported file type. Allowed: png, jpg, jpeg, gif, webp", 400)
    
    # Protect against huge uploads (we check size by peeking into stream)
    file.stream.seek(0, 2)  # seek to end
    size = file.stream.tell()
    file.stream.seek(0)     # rewind
    if size > MAX_AVATAR_BYTES:
        return error_response("File too large (max 5 MB)", 400)

    # current_user can be obtained from identity or passed by view decorator
    user = User.objects(id=current_user).first()
    if not user:
        return error_response("User not found", 404)

    filename = secure_filename(file.filename)
    result = user.set_avatar(file.stream, filename=filename, content_type=file.mimetype)
    if "error" in result:
        return error_response(result["error"], 500)

    return success_response(message="Avatar uploaded", data={"user_id": str(user.id)})

def delete_avatar(current_user) -> api_response:
    """Delete current user's avatar"""
    user = User.objects(id=current_user).first()
    if not user:
        return error_response("User not found", 404)

    if not user._avatar_image:
        return error_response("No avatar to delete", 404)

    try:
        user._avatar_image.delete()
        user._avatar_image = None
        user._avatar_image_id = None
        user.save()
        return success_response(message="Avatar deleted successfully", status_code=200)
    except Exception as e:
        return error_response("Failed to delete avatar", 500)