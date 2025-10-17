from mongoengine import Document

class UserBase(Document):
    """Base user model"""
    pass

class UserAdmin(UserBase):
    """admin user model"""
    pass

class UserStudent(UserBase):
    """student user model"""
    pass