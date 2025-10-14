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

    def to_dict(self, include_filters=True):
        result = {
            'id': str(self.id),
            'title': self.title,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
        }
        
        if include_filters:
            # Include raw filter data
            result.update({
                'semester': self.semester,
                'courses': self.courses,
                'subjects': self.subjects,
            })
            
            # Include formatted filter information for display
            result['filters'] = self._get_formatted_filters()
        
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
