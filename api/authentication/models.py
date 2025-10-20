from mongoengine import Document, StringField

class User(Document):
    """User model"""
    username = StringField(required=True)
    email = StringField(required=True, unique=True)
    password = StringField(required=True)
    matricula = StringField(required=True, unique=True)

    meta = {
        "collection": "users",        
        "allow_inheritance": True  
    }

    def to_dict(self):
        
        return {
            "id": str(self.id),
            "username": self.username,
            "email": self.email,
            "matricula":self.role,            
        }

    pass