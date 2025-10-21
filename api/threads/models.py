from mongoengine import Document, StringField, DateTimeField, ReferenceField, ListField, IntField
import mongoengine as me
from core.utils import get_brasilia_now, utc_to_brasilia

class Thread(Document): #perguntas
    title = StringField(max_length=200, required=True)
    description = StringField(max_length=500)  # Optional description field
    
    # Filter fields (optional for backward compatibility)
    semester = IntField(min_value=1, max_value=10, default=1)  # Default to 1st semester
    courses = ListField(StringField(max_length=50), default=list)  # Default to empty list
    subjects = ListField(StringField(max_length=100), default=lambda: ['Geral'])  # Default subject

    # Voting fields
    upvotes = IntField(default=0, min_value=0)
    downvotes = IntField(default=0)
    voted_users = ListField(StringField(), default=list)  # Track users who have voted

    created_at = DateTimeField(default=get_brasilia_now)
    
    meta = {
        'collection': 'threads',
        'ordering': ['-created_at']
    }

    @property
    def score(self):
        """Calculate the net score (upvotes - downvotes)"""
        return self.upvotes - self.downvotes

    def to_dict(self):
        """Convert the Thread document to a dictionary."""
        # Convert UTC stored time to Brasília time for display
        brasilia_time = utc_to_brasilia(self.created_at)
        return {
            'id': str(self.id),
            'title': self.title,
            'description': self.description,
            'semester': self.semester,
            'courses': self.courses,
            'subjects': self.subjects,
            'upvotes': self.upvotes,
            'downvotes': self.downvotes,
            'score': self.score,
            'created_at': brasilia_time.isoformat() if brasilia_time else None,
        }


class Post(Document): #respostas
    thread = ReferenceField(Thread, required=True)
    author = StringField(max_length=100, required=True, default='Anonymous')
    content = StringField(required=True)
    upvotes = IntField(default=0, min_value=0)
    downvotes = IntField(default=0)
    voted_users = ListField(StringField(), default=list)  # Track users who have voted
    created_at = DateTimeField(default=get_brasilia_now)
    
    meta = {
        'collection': 'posts',
        'ordering': ['created_at']
    }

    @property
    def score(self):
        """Calculate the net score (upvotes - downvotes)"""
        return self.upvotes - self.downvotes

    def to_dict(self):
        """Convert the Post document to a dictionary."""
        # Convert UTC stored time to Brasília time for display
        brasilia_time = utc_to_brasilia(self.created_at)
        return {
            'id': str(self.id),
            'thread_id': str(self.thread.id),
            'author': self.author,
            'content': self.content,
            'upvotes': self.upvotes,
            'downvotes': self.downvotes,
            'score': self.score,
            'created_at': brasilia_time.isoformat() if brasilia_time else None,
        }
