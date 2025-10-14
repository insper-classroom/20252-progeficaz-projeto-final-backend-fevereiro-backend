from mongoengine import Document, StringField, DateTimeField, ReferenceField, ListField, IntField
from datetime import datetime
import mongoengine as me
import pytz

# Brasília timezone (GMT-3)
BRASILIA_TZ = pytz.timezone('America/Sao_Paulo')

def get_brasilia_now():
    """Return current time in Brasília timezone converted to UTC for storage"""
    # Get current time in Brasília
    brasilia_time = datetime.now(BRASILIA_TZ)
    # Convert to UTC for consistent storage
    return brasilia_time.astimezone(pytz.UTC).replace(tzinfo=None)

def utc_to_brasilia(utc_datetime):
    """Convert UTC datetime to Brasília timezone"""
    if utc_datetime is None:
        return None
    # Make UTC datetime timezone-aware
    utc_aware = pytz.UTC.localize(utc_datetime)
    # Convert to Brasília timezone
    return utc_aware.astimezone(BRASILIA_TZ)


class Thread(Document): #perguntas
    title = StringField(max_length=200, required=True)
    description = StringField(max_length=500)  # Optional description field
    
    # Filter fields (optional for backward compatibility)
    semester = IntField(min_value=1, max_value=10, default=1)  # Default to 1st semester
    courses = ListField(StringField(max_length=50), default=list)  # Default to empty list
    subjects = ListField(StringField(max_length=100), default=lambda: ['Geral'])  # Default subject

    created_at = DateTimeField(default=get_brasilia_now)
    
    meta = {
        'collection': 'threads',
        'ordering': ['-created_at']
    }

    def to_dict(self):
        # Convert UTC stored time to Brasília time for display
        brasilia_time = utc_to_brasilia(self.created_at)
        return {
            'id': str(self.id),
            'title': self.title,
            'description': self.description,
            'semester': self.semester,
            'courses': self.courses,
            'subjects': self.subjects,
            'created_at': brasilia_time.isoformat() if brasilia_time else None,
        }


class Post(Document): #respostas
    thread = ReferenceField(Thread, required=True)
    author = StringField(max_length=100, required=True, default='Anonymous')
    content = StringField(required=True)
    created_at = DateTimeField(default=get_brasilia_now)
    
    meta = {
        'collection': 'posts',
        'ordering': ['created_at']
    }

    def to_dict(self):
        # Convert UTC stored time to Brasília time for display
        brasilia_time = utc_to_brasilia(self.created_at)
        return {
            'id': str(self.id),
            'thread_id': str(self.thread.id),
            'author': self.author,
            'content': self.content,
            'created_at': brasilia_time.isoformat() if brasilia_time else None,
        }
