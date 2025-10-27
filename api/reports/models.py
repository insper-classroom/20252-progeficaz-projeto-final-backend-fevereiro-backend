from mongoengine import Document, StringField, DateTimeField, ReferenceField
from core.utils import get_brasilia_now
from api.authentication.models import User

class Report(Document):
    """Model for content reports/denúncias"""
    _reporter = ReferenceField(User, required=True)  # Usuário que fez a denúncia
    _content_type = StringField(required=True, choices=['thread', 'post'])  # Tipo: pergunta ou resposta
    _content_id = StringField(required=True)  # ID da pergunta ou resposta
    _report_type = StringField(required=True, choices=[
        'sexual',           # Conteúdo sexual
        'violence',         # Violência
        'discrimination',   # Discriminação
        'scam',            # Enganoso/golpe
        'self_harm',       # Auto-mutilação/suicídio
        'spam',            # Spam
        'other'            # Outros
    ])
    _description = StringField(max_length=500)  # Descrição adicional (obrigatório se _report_type = 'other')
    _status = StringField(default='pending', choices=['pending', 'reviewed', 'resolved', 'dismissed'])
    _created_at = DateTimeField(default=get_brasilia_now)
    
    meta = {
        'collection': 'reports',
        'ordering': ['-_created_at']
    }

    @property
    def reporter(self):
        return self._reporter
    
    @property
    def content_type(self):
        return self._content_type
    
    @property
    def content_id(self):
        return self._content_id
    
    @property
    def report_type(self):
        return self._report_type
    
    @property
    def description(self):
        return self._description
    
    @property
    def status(self):
        return self._status

    def to_dict(self):
        """Convert the Report document to a dictionary"""
        return {
            'id': str(self.id),
            'reporter': self.reporter.username,
            'content_type': self.content_type,
            'content_id': self.content_id,
            'report_type': self.report_type,
            'description': self.description,
            'status': self.status,
            'created_at': self._created_at
        }
