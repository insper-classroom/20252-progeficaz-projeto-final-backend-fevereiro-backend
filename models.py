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

    def to_dict(self):
        return {
            'id': str(self.id),
            'semester': self.semester,
            'courses': self.courses,
            'subjects': self.subjects,
            'title': self.title,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
        }


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
