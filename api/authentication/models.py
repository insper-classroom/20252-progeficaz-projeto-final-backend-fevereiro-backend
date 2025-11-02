from mongoengine import Document, StringField, BooleanField, DateTimeField, IntField, ReferenceField
from datetime import datetime, timedelta
from core.utils import bcrypt

class User(Document):
    """User model"""
    _username = StringField(required=True, unique=True)
    _email = StringField(required=True, unique=True)
    _password = StringField(required=True)
    _created_at = DateTimeField(required=True, default=datetime.now)
    _updated_at = DateTimeField(required=True, default=datetime.now)
    _is_active = BooleanField(required=True, default=False)

    meta = {
        "collection": "users",
        "allow_inheritance": True,
        "strict": False  # Ignore extra fields in database
    }
    
    @property
    def email(self):
        return self._email
    
    @property
    def username(self):
        return self._username

    def to_dict(self):

        return {
            "id": str(self.id),
            "username": self._username,
            "email": self._email,
        }

    def set_and_hash_password(self, new_password: str):
        self._password = bcrypt.generate_password_hash(new_password).decode("utf-8")
        self._updated_at = datetime.now()
        self.save()
        
    def check_password(self, password: str) -> bool:
        return bcrypt.check_password_hash(self._password, password)
    
    def activate(self):
        self._is_active = True
        self._updated_at = datetime.now()
        self.save()
    
    def deactivate(self):
        self._is_active = False
        self._updated_at = datetime.now()
        self.save()
        

    def is_active(self) -> bool:
        return self._is_active
    
class AuthToken(Document):
    """Authentication Token model"""
    _user = ReferenceField(User, required=True)
    _token_type = StringField(required=True)
    _expiration_time = IntField(required=True)  # in seconds
    _created_at = DateTimeField(required=True, default=datetime.now)
    _used_at = DateTimeField()
    _expired_at = DateTimeField()
        
    

    meta = {
        "collection": "auth_tokens",
        "allow_inheritance": True
    }

    def to_dict(self):
        return {
            "id": str(self.id),
            "user_id": self._user_id,
            "token_type": self._token_type,
        }
    
    @property
    def type(self):
        return self._token_type
    
    def get_user(self):
        return self._user

    def is_expired(self):
        if self._expired_at:
            return True
        expiration_datetime = self._created_at + timedelta(seconds=self._expiration_time)
        if datetime.now() > expiration_datetime:
            self._expired_at = expiration_datetime
            self.save()
            return True
        return False

    def is_used(self):
        return self._used_at is not None

    def mark_used(self):
        self._used_at = datetime.now()
        self.save()