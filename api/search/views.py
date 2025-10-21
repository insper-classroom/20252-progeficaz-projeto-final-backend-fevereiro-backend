from flask import Request, request, jsonify
from core.types import api_response
from api.search.utils import get_filter_config, search_subjects, get_subject_options, get_course_options, get_semester_options, search_threads_by_title

# FILTERS views

def get_filters_config() -> api_response:
    """Get the complete filter configuration."""
    try:
        
        return jsonify(get_filter_config()), 200
    except ImportError:
        return jsonify({'error': 'Filter configuration not available'}), 500

def get_filters_by_type(filter_type: str, request: Request) -> api_response:
    """Get filter options by type."""
    if filter_type == 'semesters':
        # Get all semester options.
        try:

            return jsonify(get_semester_options()), 200
        except ImportError:
            return jsonify({'error': 'Filter configuration not available'}), 500

    elif filter_type == 'courses':
        # Get all course options.
        try:
            return jsonify(get_course_options()), 200
        except ImportError:
            return jsonify({'error': 'Filter configuration not available'}), 500
    elif filter_type == 'subjects':
        # Get subject options based on selected courses and semester
        try:
            if request is None:
                raise ValueError("Request object must be provided for subject filter")
            course_ids = request.args.getlist('courses')
            semester_id = request.args.get('semester', type=int)
            query = request.args.get('q', '').strip()
            
            if query:
                subjects = search_subjects(query, course_ids, semester_id)
            else:
                subjects = get_subject_options(course_ids, semester_id)
            
            return jsonify(subjects), 200
        except ImportError:
            return jsonify({'error': 'Filter configuration not available'}), 500

def search_threads(request: Request) -> api_response:
    """Search threads by title with optional filters."""
    try:
        query = request.args.get('q', '').strip()
        
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        # Optional filters
        semester_id = request.args.get('semester', type=int)
        course_ids = request.args.getlist('courses')
        subject_ids = request.args.getlist('subjects')
        
        results = search_threads_by_title(query, semester_id, course_ids, subject_ids)
        
        return jsonify({
            'query': query,
            'count': len(results),
            'results': results
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500