from mongoengine import Document, StringField, DateTimeField, ReferenceField, ListField, IntField
from datetime import datetime
import mongoengine as me
import pytz

# Brasília timezone (GMT-3)
BRASILIA_TZ = pytz.timezone('America/Sao_Paulo')

def get_brasilia_now():
    """Return current time in Brasília timezone"""
    return datetime.now(BRASILIA_TZ)


class Thread(Document): #perguntas
    title = StringField(max_length=200, required=True)
    description = StringField(max_length=500)  # Optional description field

    created_at = DateTimeField(default=get_brasilia_now)
    
    meta = {
        'collection': 'threads',
        'ordering': ['-created_at']
    }

    def to_dict(self):
        return {
            'id': str(self.id),
            'title': self.title,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
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
        return {
            'id': str(self.id),
            'thread_id': str(self.thread.id),
            'author': self.author,
            'content': self.content,
            'created_at': self.created_at.isoformat(),
        }
