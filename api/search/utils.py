from core.constants import FILTER_CONFIG, SEMESTERS, COURSES, SUBJECTS, DEFAULT_SUBJECTS

# Filter Configuration Utilities

def get_filter_config():
    """Return the complete filter configuration."""
    return FILTER_CONFIG

def get_semester_options():
    """Get all semester options."""
    return SEMESTERS

def get_course_options():
    """Get all course options."""
    return COURSES

def get_subject_options(course_ids=None, semester_id=None) -> list[str]:
    """Get subject options based on selected courses and semester."""
    subjects = set()
    
    if course_ids is None:
        course_ids = []
    
    # Case 1: No filters selected - show ALL subjects
    if not course_ids and not semester_id:
        for course_subjects in SUBJECTS.values():
            for semester_subjects in course_subjects.values():
                subjects.update(semester_subjects)
        subjects.update(DEFAULT_SUBJECTS)
        return sorted(list(subjects))
    
    # Case 2: Only semester selected - show all subjects for that semester
    if semester_id and not course_ids:
        for course_id in SUBJECTS.keys():
            if semester_id in SUBJECTS[course_id]:
                subjects.update(SUBJECTS[course_id][semester_id])
        subjects.update(DEFAULT_SUBJECTS)
        return sorted(list(subjects))
    
    # Case 3: Only courses selected - show all subjects for those courses
    if course_ids and not semester_id:
        for course_id in course_ids:
            if course_id in SUBJECTS:
                for semester_subjects in SUBJECTS[course_id].values():
                    subjects.update(semester_subjects)
        if not subjects:
            subjects.update(DEFAULT_SUBJECTS)
        return sorted(list(subjects))
    
    # Case 4: Both course and semester selected
    if course_ids and semester_id:
        subjects_found = False
        for course_id in course_ids:
            if course_id in SUBJECTS and semester_id in SUBJECTS[course_id]:
                subjects.update(SUBJECTS[course_id][semester_id])
                subjects_found = True
        
        if not subjects_found:
            subjects.update(DEFAULT_SUBJECTS)
        
        return sorted(list(subjects))
    
    return sorted(list(subjects))

def search_subjects(query, course_ids=None, semester_id=None) -> list[str]:
    """Search subjects by query string."""
    all_subjects = get_subject_options(course_ids, semester_id)
    query_lower = query.lower()
    
    return [subject for subject in all_subjects if query_lower in subject.lower()]

def search_threads_by_title(query: str, semester_id=None, course_ids=None, subject_ids=None):
    """Search threads by title with optional filters."""
    from api.threads.models import Thread, Post
    
    if not query or not query.strip():
        return []
    
    # Build the search query
    search_query = {
        '_title': {'$regex': query, '$options': 'i'}  # Case-insensitive search - use _title not title
    }
    
    # Add optional filters
    if semester_id:
        search_query['semester'] = semester_id
    
    if course_ids:
        search_query['courses'] = {'$in': course_ids}
    
    if subject_ids:
        search_query['subjects'] = {'$in': subject_ids}
    
    # Execute search
    threads = Thread.objects(__raw__=search_query).order_by('-_created_at')
    
    # Format results
    results = []
    for thread in threads:
        # Count posts for this thread
        post_count = Post.objects(_thread=thread).count()
        
        results.append({
            'id': str(thread.id),
            'title': thread._title,
            'description': thread._description if thread._description else '',
            'author': thread.author.username if thread.author else 'Unknown',
            'semester': thread.semester,
            'courses': thread.courses if thread.courses else [],
            'subjects': thread.subjects if thread.subjects else [],
            'score': thread.score,
            'created_at': thread._created_at.isoformat() if thread._created_at else None,
            'post_count': post_count
        })
    
    return results