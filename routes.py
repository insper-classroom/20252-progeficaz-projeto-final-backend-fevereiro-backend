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


@api_bp.route('/filters/active', methods=['POST'])
def get_active_filters():
    """Get formatted information about active filters for display."""
    from filter_config import SEMESTERS, COURSES, get_subject_options
    
    data = request.get_json() or {}
    semesters = data.get('semesters', [])
    courses = data.get('courses', [])
    subjects = data.get('subjects', [])
    
    # Format active filters with readable names
    active_filters = {
        'semesters': [],
        'courses': [],
        'subjects': subjects or [],  # Subjects are already readable names
        'has_active_filters': bool(semesters or courses or subjects)
    }
    
    # Format semesters
    if semesters:
        semester_dict = {s['id']: s['name'] for s in SEMESTERS}
        for semester_id in semesters:
            try:
                semester_int = int(semester_id)
                semester_name = semester_dict.get(semester_int, f"{semester_int}º Semestre")
                active_filters['semesters'].append({
                    'id': semester_int,
                    'name': semester_name
                })
            except (ValueError, TypeError):
                continue
    
    # Format courses
    if courses:
        course_dict = {c['id']: c['name'] for c in COURSES}
        for course_id in courses:
            if course_id:
                course_name = course_dict.get(course_id, course_id)
                active_filters['courses'].append({
                    'id': course_id,
                    'name': course_name
                })
    
    return jsonify(active_filters)


@api_bp.route('/threads/filter', methods=['POST'])
def filter_threads():
    """Filter threads with POST request for complex filtering."""
    data = request.get_json() or {}
    
    # Get filter parameters from POST body - all are optional
    semesters = data.get('semesters', [])  # List of semester IDs
    courses = data.get('courses', [])      # List of course IDs
    subjects = data.get('subjects', [])    # List of subject names
    
    # Debug logging
    print(f"DEBUG: POST filtering threads - semesters={semesters}, courses={courses}, subjects={subjects}")
    
    # Build query - only add filters if they have values
    query = {}
    
    # Semester filter - support multiple semesters (exact match for integer field)
    if semesters:
        try:
            semester_ints = [int(s) for s in semesters if s is not None and str(s).strip()]
            if semester_ints:
                if len(semester_ints) == 1:
                    query['semester'] = semester_ints[0]
                else:
                    query['semester__in'] = semester_ints
        except (ValueError, TypeError):
            print(f"DEBUG: Invalid semester values: {semesters}")
    
    # Course filter - multiple courses (array field)
    if courses:
        course_list = [c for c in courses if c and str(c).strip()]
        if course_list:
            if len(course_list) == 1:
                query['courses__contains'] = course_list[0]
            else:
                query['courses__in'] = course_list
    
    # Subject filter - multiple subjects (array field)
    if subjects:
        subject_list = [s for s in subjects if s and str(s).strip()]
        if subject_list:
            if len(subject_list) == 1:
                query['subjects__contains'] = subject_list[0]
            else:
                query['subjects__in'] = subject_list
    
    print(f"DEBUG: Final POST query: {query}")
    
    # Execute query
    try:
        if query:
            threads = Thread.objects(**query).order_by('-created_at')
            print(f"DEBUG: Found {len(threads)} filtered threads (POST)")
        else:
            threads = Thread.objects().order_by('-created_at')
            print(f"DEBUG: No filters applied (POST), showing all {len(threads)} threads")
        
        # Debug: Print some thread details
        if threads:
            print(f"DEBUG: Sample filtered thread data:")
            for i, thread in enumerate(threads[:2]):
                print(f"  Thread {i+1}: {thread.title}")
                print(f"    Semester: {thread.semester}")
                print(f"    Courses: {thread.courses}")
                print(f"    Subjects: {thread.subjects}")
    
    except Exception as e:
        print(f"DEBUG: POST Query error: {e}")
        threads = []
    
    # Format active filters for display
    from filter_config import SEMESTERS, COURSES
    active_filters = {
        'semesters': [],
        'courses': [],
        'subjects': subjects or [],
        'has_active_filters': bool(semesters or courses or subjects)
    }
    
    # Format semesters with names
    if semesters:
        semester_dict = {s['id']: s['name'] for s in SEMESTERS}
        for semester_id in semesters:
            try:
                semester_int = int(semester_id)
                semester_name = semester_dict.get(semester_int, f"{semester_int}º Semestre")
                active_filters['semesters'].append({
                    'id': semester_int,
                    'name': semester_name
                })
            except (ValueError, TypeError):
                continue
    
    # Format courses with names
    if courses:
        course_dict = {c['id']: c['name'] for c in COURSES}
        for course_id in courses:
            if course_id:
                course_name = course_dict.get(course_id, course_id)
                active_filters['courses'].append({
                    'id': course_id,
                    'name': course_name
                })
    
    return jsonify({
        'threads': [t.to_dict(mode='full') for t in threads],
        'active_filters': active_filters,
        'total_count': len(threads),
        'query_applied': query  # For debugging
    })


@api_bp.route('/threads', methods=['GET'])
def list_threads():
    """List threads with optional filtering."""
    # Get filter parameters - all are optional
    semesters = request.args.getlist('semester')
    courses = request.args.getlist('courses')
    subjects = request.args.getlist('subjects')
    
    # Get display mode parameter
    mode = request.args.get('mode', 'list_with_filters')  # Default to include hidden filters
    
    # Debug logging
    print(f"DEBUG: Filtering threads - semesters={semesters}, courses={courses}, subjects={subjects}, mode={mode}")
    
    # Build query - only add filters if they have values
    query = {}
    
    # Semester filter - support multiple semesters (exact match for integer field)
    if semesters:
        try:
            semester_ints = [int(s) for s in semesters if s]
            if semester_ints:
                if len(semester_ints) == 1:
                    query['semester'] = semester_ints[0]
                else:
                    query['semester__in'] = semester_ints
        except ValueError:
            print(f"DEBUG: Invalid semester values: {semesters}")
    
    # Course filter - multiple courses (array field - any thread that has ANY of these courses)
    if courses:
        course_list = [c for c in courses if c]
        if course_list:
            if len(course_list) == 1:
                query['courses__contains'] = course_list[0]  # Thread's courses array contains this course
            else:
                query['courses__in'] = course_list  # Thread's courses array contains any of these courses
    
    # Subject filter - multiple subjects (array field - any thread that has ANY of these subjects)
    if subjects:
        subject_list = [s for s in subjects if s]
        if subject_list:
            if len(subject_list) == 1:
                query['subjects__contains'] = subject_list[0]  # Thread's subjects array contains this subject
            else:
                query['subjects__in'] = subject_list  # Thread's subjects array contains any of these subjects
    
    print(f"DEBUG: Final query: {query}")
    
    # Execute query
    try:
        if query:
            threads = Thread.objects(**query).order_by('-created_at')
            print(f"DEBUG: Found {len(threads)} filtered threads")
        else:
            threads = Thread.objects().order_by('-created_at')
            print(f"DEBUG: No filters applied, showing all {len(threads)} threads")
        
        # Debug: Print some thread details to verify data
        if threads:
            print(f"DEBUG: Sample thread data:")
            for i, thread in enumerate(threads[:2]):  # Show first 2 threads
                print(f"  Thread {i+1}: {thread.title}")
                print(f"    Semester: {thread.semester}")
                print(f"    Courses: {thread.courses}")
                print(f"    Subjects: {thread.subjects}")
        
    except Exception as e:
        print(f"DEBUG: Query error: {e}")
        threads = []
    
    # Return threads based on mode
    if mode == 'list':
        # Pure main page - no description, no filters (minimal)
        return jsonify([t.to_dict(mode='list') for t in threads])
    elif mode == 'list_with_filters':
        # Main page with hidden filter data for frontend logic
        return jsonify([t.to_dict(mode='list_with_filters') for t in threads])
    else:
        # Filtered view - include visible filters but no description
        return jsonify([t.to_dict(mode='full') for t in threads])


@api_bp.route('/threads/<thread_id>', methods=['GET'])
def get_thread(thread_id):
    try:
        # Debug logging
        print(f"DEBUG: Attempting to get thread with ID: {thread_id}")
        
        # Validate ObjectId format
        if not thread_id or len(thread_id) != 24:
            print(f"DEBUG: Invalid thread_id format: {thread_id}")
            return jsonify({'error': 'Invalid thread ID format'}), 400
        
        # Try to get the thread
        thread = Thread.objects.get(id=thread_id)
        print(f"DEBUG: Found thread: {thread.title}")
        
        posts = Post.objects(thread=thread).order_by('created_at')
        print(f"DEBUG: Found {len(posts)} posts for thread")
        
        # Detail view - include everything
        data = thread.to_dict(mode='detail')
        data['posts'] = [p.to_dict() for p in posts]
        
        return jsonify(data)
        
    except DoesNotExist:
        print(f"DEBUG: Thread not found with ID: {thread_id}")
        return jsonify({'error': 'Thread not found'}), 404
    except ValidationError as e:
        print(f"DEBUG: Validation error: {str(e)}")
        return jsonify({'error': 'Invalid thread ID'}), 400
    except Exception as e:
        print(f"DEBUG: Unexpected error: {str(e)} (type: {type(e)})")
        return jsonify({'error': 'Invalid thread ID'}), 400


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
        return jsonify(thread.to_dict(mode='detail')), 201  # Return full details when creating
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400


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
        return jsonify(thread.to_dict(mode='detail'))  # Return full details when updating
    except DoesNotExist:
        return jsonify({'error': 'Thread not found'}), 404
    except ValidationError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        return jsonify({'error': 'Invalid thread ID'}), 400


@api_bp.route('/threads/clear-filters', methods=['GET'])
def clear_filters():
    """Get all threads without any filters (same as GET /threads with no params)."""
    threads = Thread.objects().order_by('-created_at')
    print(f"DEBUG: Showing all {len(threads)} threads (filters cleared)")
    
    return jsonify({
        'threads': [t.to_dict(mode='full') for t in threads],  # Show filters when clearing filters
        'filters_applied': {
            'semesters': [],
            'courses': [],
            'subjects': []
        },
        'total_count': len(threads)
    })


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


@api_bp.route('/threads/debug', methods=['GET'])
def debug_threads():
    """Debug endpoint to see all threads and their filter data."""
    try:
        threads = Thread.objects().order_by('-created_at')
        debug_data = []
        
        for thread in threads:
            debug_data.append({
                'id': str(thread.id),
                'title': thread.title,
                'semester': thread.semester,
                'courses': thread.courses,
                'subjects': thread.subjects,
                'created_at': thread.created_at.isoformat()
            })
        
        return jsonify({
            'total_threads': len(threads),
            'threads': debug_data
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
