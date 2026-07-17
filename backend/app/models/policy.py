import uuid
from datetime import datetime
from app.database import db

class Policy(db.Model):
    __tablename__ = 'policies'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), nullable=False)  # GDPR, ISO27001, SOC2, Internal, Vendor, Custom
    s3_key = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)  # PDF, DOCX
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    chunks = db.relationship('PolicyChunk', backref='policy', lazy=True, cascade="all, delete-orphan")
    findings = db.relationship('AIFinding', backref='policy', lazy=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'category': self.category,
            's3_key': self.s3_key,
            'file_type': self.file_type,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class PolicyChunk(db.Model):
    __tablename__ = 'policy_chunks'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    policy_id = db.Column(db.String(36), db.ForeignKey('policies.id', ondelete='CASCADE'), nullable=False)
    chunk_text = db.Column(db.Text, nullable=False)
    page_number = db.Column(db.Integer, nullable=False)
    paragraph_number = db.Column(db.Integer, nullable=False)
    chunk_position = db.Column(db.Integer, nullable=False)
    qdrant_id = db.Column(db.String(36), nullable=True)  # Store mapped Qdrant UUID
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self):
        return {
            'id': self.id,
            'policy_id': self.policy_id,
            'chunk_text': self.chunk_text,
            'page_number': self.page_number,
            'paragraph_number': self.paragraph_number,
            'chunk_position': self.chunk_position,
            'qdrant_id': self.qdrant_id
        }
