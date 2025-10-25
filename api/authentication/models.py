from mongoengine import Document, StringField, BooleanField, DateTimeField, IntField
from datetime import datetime, timedelta
from core.utils import bcrypt

class User(Document):
    """User model"""
    username = StringField(required=True, unique=True)
    email = StringField(required=True, unique=True)
    _password = StringField(required=True)
    _created_at = DateTimeField(required=True, default=datetime.now)
    _updated_at = DateTimeField(required=True, default=datetime.now)
    _is_active = BooleanField(required=True, default=False)

    meta = {
        "collection": "users",
        "allow_inheritance": True
    }

    def to_dict(self):

        return {
            "id": str(self.id),
            "username": self.username,
            "email": self.email,
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
    _user_id = StringField(required=True)
    token_type = StringField(required=True)
    expiration_time = IntField(required=True)  # in seconds
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
            "token_type": self.token_type,
        }
        
    def get_user(self):
        return User.objects.get(id=self._user_id)
    
    def is_expired(self):
        if self._expired_at:
            return True
        expiration_datetime = self._created_at + timedelta(seconds=self.expiration_time)
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