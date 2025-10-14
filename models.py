from mongoengine import Document, StringField, DateTimeField, ReferenceField, ListField, IntField
from datetime import datetime
import mongoengine as me


class Thread(Document): #perguntas
    title = StringField(max_length=200, required=True)
    description = StringField(max_length=500)  # Optional description field
    
    # Filter fields
    semester = IntField(required=True, min_value=1, max_value=10)  # Required, single selection
    courses = ListField(StringField(max_length=50))  # Optional, multiple selection
    subjects = ListField(StringField(max_length=100), required=True)  # Required, multiple selection

    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'threads',
        'ordering': ['-created_at']
    }

    def to_dict(self, include_filters=True, include_description=True, mode='full'):
        """
        Convert thread to dictionary with different display modes.
        
        Args:
            include_filters (bool): Include filter information
            include_description (bool): Include description field
            mode (str): Display mode - 'list', 'list_with_filters', 'full', or 'detail'
                - 'list': Minimal info for main page listing (no description, no filters)
                - 'list_with_filters': Main page with hidden filter data (for filtering logic)
                - 'full': Complete info including filters but condensed
                - 'detail': Full detail view with all information
        """
        result = {
            'id': str(self.id),
            'title': self.title,
            'created_at': self.created_at.isoformat(),
        }
        
        # Mode-based inclusion of fields
        if mode == 'list':
            # Main page listing - minimal information only
            return result
        
        elif mode == 'list_with_filters':
            # Main page listing with hidden filter data for frontend filtering logic
            result.update({
                'semester': self.semester,
                'courses': self.courses,
                'subjects': self.subjects,
                '_filters_hidden': True,  # Flag to indicate filters are for logic, not display
                'filters': self._get_formatted_filters()
            })
            return result
        
        elif mode == 'full':
            # Standard listing with filters but no description
            if include_filters:
                result.update({
                    'semester': self.semester,
                    'courses': self.courses,
                    'subjects': self.subjects,
                    'filters': self._get_formatted_filters()
                })
            return result
        
        else:  # mode == 'detail' or default
            # Complete information for detail view
            if include_description:
                result['description'] = self.description
            
            if include_filters:
                result.update({
                    'semester': self.semester,
                    'courses': self.courses,
                    'subjects': self.subjects,
                    'filters': self._get_formatted_filters()
                })
            
            return result

    def _get_formatted_filters(self):
        """Get formatted filter information for display"""
        try:
            from filter_config import SEMESTERS, COURSES
        except ImportError:
            print("DEBUG: Could not import filter_config")
            # Fallback without formatted names
            return {
                'semester': {
                    'id': self.semester,
                    'name': f"{self.semester}º Semestre"
                },
                'courses': [{'id': course_id, 'name': course_id} for course_id in (self.courses or [])],
                'subjects': self.subjects or []
            }
        
        formatted = {
            'semester': {
                'id': self.semester,
                'name': f"{self.semester}º Semestre"
            },
            'courses': [],
            'subjects': self.subjects or []
        }
        
        # Format courses with names
        if self.courses:
            try:
                course_dict = {c['id']: c['name'] for c in COURSES}
                for course_id in self.courses:
                    course_name = course_dict.get(course_id, course_id)
                    formatted['courses'].append({
                        'id': course_id,
                        'name': course_name
                    })
            except Exception as e:
                print(f"DEBUG: Error formatting courses: {e}")
                # Fallback to IDs only
                formatted['courses'] = [{'id': course_id, 'name': course_id} for course_id in self.courses]
        
        return formatted


class Post(Document): #respostas
    thread = ReferenceField(Thread, required=True)
    author = StringField(max_length=100, required=True, default='Anonymous')
    content = StringField(required=True)
    created_at = DateTimeField(default=datetime.utcnow)
    
    meta = {
        'collection': 'posts',
        'ordering': ['created_at']
    }

    def to_dict(self):
        return {
            'id': str(self.id),
            'thread_id': str(self.thread.id),
            'author': self.author,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
        }
