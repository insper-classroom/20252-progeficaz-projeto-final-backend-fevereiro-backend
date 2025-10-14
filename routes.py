from flask import Blueprint, request, jsonify, current_app
from models import Thread, Post
from mongoengine.errors import DoesNotExist, ValidationError
from bson import ObjectId
from filter_config import (
    get_filter_config, get_semester_options, get_course_options, 
    get_subject_options, search_subjects
)

api_bp = Blueprint('api', __name__)


# Filter endpoints
@api_bp.route('/filters/config', methods=['GET'])
def get_filters_config():
    """Get the complete filter configuration."""
    return jsonify(get_filter_config())


@api_bp.route('/filters/semesters', methods=['GET'])
def get_semesters():
    """Get all semester options."""
    return jsonify(get_semester_options())


@api_bp.route('/filters/courses', methods=['GET'])
def get_courses():
    """Get all course options."""
    return jsonify(get_course_options())


@api_bp.route('/filters/subjects', methods=['GET'])
def get_subjects():
    """Get subject options based on course and semester filters."""
    course_ids = request.args.getlist('courses')
    semester_id = request.args.get('semester', type=int)
    query = request.args.get('q', '').strip()
    
    # Debug logging (remove in production)
    print(f"DEBUG: course_ids={course_ids}, semester_id={semester_id}, query='{query}'")
    
    if query:
        subjects = search_subjects(query, course_ids, semester_id)
    else:
        subjects = get_subject_options(course_ids, semester_id)
    
    # Debug logging (remove in production)
    print(f"DEBUG: Found {len(subjects)} subjects")
    
    return jsonify(subjects)


@api_bp.route('/threads', methods=['GET'])
def list_threads():
    """List threads with optional filtering."""
    # Get filter parameters
    semester = request.args.get('semester', type=int)
    courses = request.args.getlist('courses')
    subjects = request.args.getlist('subjects')
    
    # Build query
    query = {}
    if semester:
        query['semester'] = semester
    if courses:
        query['courses__in'] = courses
    if subjects:
        query['subjects__in'] = subjects
    
    threads = Thread.objects(**query).order_by('-created_at')
    return jsonify([t.to_dict() for t in threads])


@api_bp.route('/threads', methods=['POST'])
def create_thread():
    data = request.get_json() or {}
    title = data.get('title')
    description = data.get('description')
    semester = data.get('semester')
    courses = data.get('courses', [])
    subjects = data.get('subjects', [])
    
    # Validate required fields
    if not title:
        return jsonify({'error': 'title required'}), 400
    if not semester:
        return jsonify({'error': 'semester required'}), 400
    if not subjects:
        return jsonify({'error': 'at least one subject required'}), 400
    
    # Validate semester range
    if not (1 <= semester <= 10):
        return jsonify({'error': 'semester must be between 1 and 10'}), 400
    
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
    """Update a thread's title, description, or filters"""
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
        if 'semester' in data:
            if not (1 <= data['semester'] <= 10):
                return jsonify({'error': 'semester must be between 1 and 10'}), 400
            thread.semester = data['semester']
        if 'courses' in data:
            thread.courses = data['courses']
        if 'subjects' in data:
            if not data['subjects']:
                return jsonify({'error': 'at least one subject required'}), 400
            thread.subjects = data['subjects']
        
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
