from mongoengine import Document, StringField, DateTimeField, ReferenceField, ListField, IntField, ReferenceField
import mongoengine as me
from core.utils import get_brasilia_now, utc_to_brasilia
from api.authentication.models import User

class Thread(Document): #perguntas
    author = ReferenceField(User, required=True)
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
            'author': self.author.username,
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
    author = ReferenceField(User, required=True)
    content = StringField(required=True)
    pinned = me.BooleanField(default=False)  # Pin status for the post
    upvotes = IntField(default=0, min_value=0)
    downvotes = IntField(default=0)
    voted_users = ListField(StringField(), default=list)  # Track users who have voted
    created_at = DateTimeField(default=get_brasilia_now)
    
    meta = {
        'collection': 'posts',
        'ordering': ['-pinned', 'created_at']  # Pinned posts first, then by creation date
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
            'author': self.author.username,
            'content': self.content,
            'pinned': self.pinned,
            'upvotes': self.upvotes,
            'downvotes': self.downvotes,
            'score': self.score,
            'created_at': brasilia_time.isoformat() if brasilia_time else None,
        }
