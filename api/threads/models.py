from mongoengine import Document, StringField, DateTimeField, ReferenceField, ListField, IntField, ReferenceField
import mongoengine as me
from core.utils import get_brasilia_now, utc_to_brasilia
from api.authentication.models import User

class Thread(Document): #perguntas
    _title = StringField(max_length=200, required=True)
    _description = StringField(max_length=500)  # Optional description field
    _author = ReferenceField(User, required=True)
    
    # Filter fields (optional for backward compatibility)
    semester = IntField(min_value=1, max_value=10, default=1)  # Default to 1st semester
    courses = ListField(StringField(max_length=50), default=list)  # Default to empty list
    subjects = ListField(StringField(max_length=100), default=lambda: ['Geral'])  # Default subject

    # Voting fields
    _upvoted_users = ListField(StringField(), default=list)  # Track users who have voted
    _downvoted_users = ListField(StringField(), default=list)  # Track users who have voted
    _score = IntField(default=0)  # Cached score for performance


    _created_at = DateTimeField(default=get_brasilia_now)
    _updated_at = DateTimeField(default=get_brasilia_now)
    
    
    meta = {
        'collection': 'threads',
        'ordering': ['-_score', '-_created_at']
    }

    @property
    def score(self):
        """Calculate the net score (upvotes - downvotes)"""
        new_score = len(self._upvoted_users) - len(self._downvoted_users)
        if new_score != self._score:
            self._score = new_score
            self.save()
        return self._score
    
    @property
    def author(self):
        return self._author
    
    def update(self, data: dict):
        """Update thread fields"""
        allowed_fields = ['title', 'description', 'semester', 'courses', 'subjects']
        for field in allowed_fields:
            if field in data:
                setattr(self, f'_{field}' if field in ['title', 'description'] else field, data[field])
        self._updated_at = get_brasilia_now()
        self.save()
    
    def upvote(self, user_id: str):
        """Add an upvote from a user"""
        if user_id == self.author.id:
            return  # Prevent users from upvoting their own posts
        if user_id in self._downvoted_users:
            self._downvoted_users.remove(user_id)
        if user_id in self._upvoted_users:
            self._upvoted_users.remove(user_id)
        else:
            self._upvoted_users.append(user_id)
        self.save()

    def downvote(self, user_id: str):
        """Add a downvote from a user"""
        if user_id == self.author.id:
            return  # Prevent users from downvoting their own posts
        if user_id in self._upvoted_users:
            self._upvoted_users.remove(user_id)
        if user_id in self._downvoted_users:
            self._downvoted_users.remove(user_id)
        else:
            self._downvoted_users.append(user_id)
        self.save()
        return 
    
    def to_dict(self, user_id=None):
        """Convert the Thread document to a dictionary."""
        try:
            # Convert UTC stored time to Brasília time for display
            thread_dict = {
                'id': str(self.id),
                'author': self.author.username if self.author else 'Unknown',
                'title': self._title,
                'description': self._description if self._description else '',
                'semester': self.semester,
                'courses': self.courses if self.courses else [],
                'subjects': self.subjects if self.subjects else [],
                'score': self.score,
                'created_at': self._created_at.isoformat() if self._created_at else None,
            }
            if user_id:
                if str(user_id) in self._upvoted_users:
                    thread_dict['user_vote'] = 'upvote'
                elif str(user_id) in self._downvoted_users:
                    thread_dict['user_vote'] = 'downvote'
                else:
                    thread_dict['user_vote'] = None
            return thread_dict
        except Exception as e:
            print(f"Error in Thread.to_dict: {e}")
            import traceback
            traceback.print_exc()
            raise

class Post(Document): #respostas
    _content = StringField(required=True)
    _author = ReferenceField(User, required=True)
    _created_at = DateTimeField(default=get_brasilia_now)
    _updated_at = DateTimeField(default=get_brasilia_now)
    _thread = ReferenceField(Thread, required=True)
    _pinned = me.BooleanField(default=False)  # Pin status for the post
    _upvoted_users = ListField(StringField(), default=list)  # Track users who have voted
    _downvoted_users = ListField(StringField(), default=list)  # Track users who have voted
    _score = IntField(default=0)  # Cached score for performance
    
    
    meta = {
        'collection': 'posts',
        'ordering': ['-_pinned', '-_score', '_created_at']  # Pinned posts first, then by creation date
    }

    @property
    def score(self):
        """Calculate the net score (upvotes - downvotes)""" 
        new_score = len(self._upvoted_users) - len(self._downvoted_users)
        if new_score != self._score:
            self._score = new_score
            self.save()
        return self._score
    
    @property
    def author(self):
        return self._author

    @property
    def thread(self):
        return self._thread
    
    @property
    def pinned(self):
        return self._pinned

    def update_content(self, new_content: str):
        """Update the content of the post"""
        self._content = new_content
        self._updated_at = get_brasilia_now()
        self.save()
    
    def upvote(self, user_id: str):
        """Add an upvote from a user"""
        if user_id == self.author.id:
            return  # Prevent users from upvoting their own posts
        if user_id in self._downvoted_users:
            self._downvoted_users.remove(user_id)
        if user_id in self._upvoted_users:
            self._upvoted_users.remove(user_id)
        else:
            self._upvoted_users.append(user_id)
        self.save()

    def downvote(self, user_id: str):
        """Add a downvote from a user"""
        if user_id == self.author.id:
            return  # Prevent users from downvoting their own posts
        if user_id in self._upvoted_users:
            self._upvoted_users.remove(user_id)
        if user_id in self._downvoted_users:
            self._downvoted_users.remove(user_id)
        else:
            self._downvoted_users.append(user_id)
        self.save()
        return 
        
    def pin(self):
        """Pin the post"""
        if not self._pinned:
            self._pinned = True
            self.save()
    
    def unpin(self):
        """Unpin the post"""
        if self._pinned:
            self._pinned = False
            self.save()
    
    def get_thread(self):
        """Get the thread associated with this post"""
        return self._thread

    def to_dict(self, user_id=None):
        """Convert the Post document to a dictionary."""
        try:
            # Convert UTC stored time to Brasília time for display
            post_dict = {
                'id': str(self.id),
                'thread_id': str(self._thread.id) if self._thread else None,
                'author': self._author.username if self._author else 'Unknown',
                'content': self._content,
                'pinned': self._pinned,
                'score': self.score,
                'created_at': self._created_at.isoformat() if self._created_at else None,
                'updated_at': self._updated_at.isoformat() if self._updated_at else None,
            }
            if user_id:
                if str(user_id) in self._upvoted_users:
                    post_dict['user_vote'] = 'upvote'
                elif str(user_id) in self._downvoted_users:
                    post_dict['user_vote'] = 'downvote'
                else:
                    post_dict['user_vote'] = None
            return post_dict
        except Exception as e:
            print(f"Error in Post.to_dict: {e}")
            import traceback
            traceback.print_exc()
            raise
