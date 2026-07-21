import uuid
from datetime import datetime
from app.database import db

class Contract(db.Model):
    __tablename__ = 'contracts'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    department_id = db.Column(db.String(36), db.ForeignKey('departments.id', ondelete='SET NULL'), nullable=True)
    owner_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    status = db.Column(db.String(30), default='Draft')  # Draft, Pending Review, Approved, Rejected, Archived
    current_version = db.Column(db.Integer, default=1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # Relationships
    versions = db.relationship('ContractVersion', backref='contract', lazy=True, cascade="all, delete-orphan")
    reports = db.relationship('Report', backref='contract', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'department_id': self.department_id,
            'department_name': self.department.name if self.department else None,
            'owner_id': self.owner_id,
            'owner_name': self.owner.full_name if self.owner else None,
            'status': self.status,
            'current_version': self.current_version,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }


class ContractVersion(db.Model):
    __tablename__ = 'contract_versions'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    contract_id = db.Column(db.String(36), db.ForeignKey('contracts.id', ondelete='CASCADE'), nullable=False)
    version_number = db.Column(db.Integer, nullable=False)
    s3_key = db.Column(db.String(500), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)  # PDF, DOCX
    status = db.Column(db.String(30), default='Uploaded')  # Uploaded, Processing, Analyzed, Error
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    # Relationships
    chunks = db.relationship('ContractChunk', backref='version', lazy=True, cascade="all, delete-orphan")
    findings = db.relationship('AIFinding', backref='version', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            'id': self.id,
            'contract_id': self.contract_id,
            'version_number': self.version_number,
            's3_key': self.s3_key,
            'file_type': self.file_type,
            'status': self.status,
            'created_at': self.created_at.isoformat()
        }


class ContractChunk(db.Model):
    __tablename__ = 'contract_chunks'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    version_id = db.Column(db.String(36), db.ForeignKey('contract_versions.id', ondelete='CASCADE'), nullable=False)
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
            'version_id': self.version_id,
            'chunk_text': self.chunk_text,
            'page_number': self.page_number,
            'paragraph_number': self.paragraph_number,
            'chunk_position': self.chunk_position,
            'qdrant_id': self.qdrant_id
        }
