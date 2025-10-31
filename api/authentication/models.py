from io import BytesIO
from mongoengine import Document, StringField, BooleanField, DateTimeField, IntField, ReferenceField, EmailField, ImageField
from datetime import datetime, timedelta
from core.utils import bcrypt

class User(Document):
    """User model"""
    _username = StringField(required=True, unique=True)
    _avatar_image = ImageField(required=False)
    _email = EmailField(required=True, unique=True)
    _password = StringField(required=True)
    _created_at = DateTimeField(required=True, default=datetime.now)
    _updated_at = DateTimeField(required=True, default=datetime.now)
    _is_active = BooleanField(required=True, default=False)
    _points = IntField(default=0)
    _total_points = IntField(default=0)
    _last_reset_date = DateTimeField(default=datetime.now)

    meta = {
        "collection": "users",
        "allow_inheritance": True
    }
    
    @property
    def email(self):
        return self._email
    
    @property
    def username(self):
        return self._username
    
    @property
    def points(self):
        return self._points
    
    @property
    def total_points(self):
        return self._total_points

    def to_dict(self):
        return {
            "id": str(self.id),
            "username": self._username,
            "email": self._email,
            "points": self._points,
            "total_points": self._total_points,
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
    
    def check_and_reset_points(self):
        """Check if a month has passed and reset points if needed (resets on the 1st of each month)"""
        now = datetime.now()
        last_reset = self._last_reset_date
        
        # Check if we're in a new month and past the 1st, or if we never reset this month
        if (last_reset.year < now.year or 
            (last_reset.year == now.year and last_reset.month < now.month)):
            self._points = 0
            self._last_reset_date = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            self.save()
    
    def increment_points(self, amount=1):
        """Increment user points, checking for monthly reset first"""
        self.check_and_reset_points()
        self._points += amount
        self._total_points += amount
        self._updated_at = datetime.now()
        self.save()

    
    def set_avatar(self, fileobj, filename=None, content_type=None):
        """
        fileobj: file-like object (stream) or bytes
        Stores avatar to GridFS (self._avatar_image is the GridFS proxy)
        - Replaces the existing avatar file in GridFS if present (deletes old file)
        - Updates metadata on user
        Returns dict with 'message' or 'error'
        """
        try:
            # Accept bytes (convert to BytesIO) or file-like
            if isinstance(fileobj, (bytes, bytearray)):
                file_stream = BytesIO(fileobj)
            else:
                # assume fileobj is file-like and at correct position
                file_stream = fileobj

            # Optional: delete previous avatar gridfs file to avoid orphaned files
            if self._avatar_image:
                self._avatar_image.delete()

            # put the new file; many GridFS proxies accept a file-like object
            put_result = self._avatar_image.put(
                file_stream,
                filename=filename,
                content_type=content_type,
            )

            # store reference to avatar file id (adjust field names for your ODM)
            self._avatar_image_id = put_result if put_result else getattr(self._avatar_image, "id", None)
            self._updated_at = datetime.now()
            self.save()
            return {"message": "Avatar updated successfully"}
        except Exception as e:
            return {"error": str(e)}

    def get_avatar(self):
        """Return GridFSProxy or None"""
        if self._avatar_image:
            return self._avatar_image
        return None

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