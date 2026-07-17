import uuid
from datetime import datetime
from app.database import db

class AIFinding(db.Model):
    __tablename__ = 'ai_findings'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    version_id = db.Column(db.String(36), db.ForeignKey('contract_versions.id', ondelete='CASCADE'), nullable=False)
    category = db.Column(db.String(50), nullable=False)  # Missing Clause, GDPR, Payment, Liability, etc.
    risk_level = db.Column(db.String(20), nullable=False)  # High, Medium, Low
    title = db.Column(db.String(200), nullable=False)
    explanation = db.Column(db.Text, nullable=False)
    business_impact = db.Column(db.Text, nullable=True)
    recommendation = db.Column(db.Text, nullable=True)
    confidence_score = db.Column(db.Float, nullable=False, default=1.0)
    
    # Citation / Evidence Fields
    contract_page_number = db.Column(db.Integer, nullable=True)
    contract_paragraph_number = db.Column(db.Integer, nullable=True)
    policy_id = db.Column(db.String(36), db.ForeignKey('policies.id', ondelete='SET NULL'), nullable=True)
    policy_page_number = db.Column(db.Integer, nullable=True)
    policy_paragraph_number = db.Column(db.Integer, nullable=True)
    matching_clause_text = db.Column(db.Text, nullable=True)
    matching_policy_text = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self):
        return {
            'id': self.id,
            'version_id': self.version_id,
            'category': self.category,
            'risk_level': self.risk_level,
            'title': self.title,
            'explanation': self.explanation,
            'business_impact': self.business_impact,
            'recommendation': self.recommendation,
            'confidence_score': self.confidence_score,
            'contract_page_number': self.contract_page_number,
            'contract_paragraph_number': self.contract_paragraph_number,
            'policy_id': self.policy_id,
            'policy_name': self.policy.name if self.policy else None,
            'policy_page_number': self.policy_page_number,
            'policy_paragraph_number': self.policy_paragraph_number,
            'matching_clause_text': self.matching_clause_text,
            'matching_policy_text': self.matching_policy_text,
            'created_at': self.created_at.isoformat()
        }


class AuditLog(db.Model):
    __tablename__ = 'audit_logs'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    action = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)
    details = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'user_name': self.user.full_name if self.user else 'System',
            'action': self.action,
            'ip_address': self.ip_address,
            'details': self.details,
            'created_at': self.created_at.isoformat()
        }


class Report(db.Model):
    __tablename__ = 'reports'

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)
    report_type = db.Column(db.String(50), nullable=False)  # Executive Summary, Compliance Report, Risk Heatmap, Audit Trail
    s3_key = db.Column(db.String(500), nullable=False)
    created_by = db.Column(db.String(36), db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    contract_id = db.Column(db.String(36), db.ForeignKey('contracts.id', ondelete='CASCADE'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'report_type': self.report_type,
            's3_key': self.s3_key,
            'created_by': self.created_by,
            'creator_name': self.creator.full_name if self.creator else 'System',
            'contract_id': self.contract_id,
            'created_at': self.created_at.isoformat()
        }
