from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required
from sqlalchemy import func
from app.database import db
from app.models.contract import Contract, ContractVersion
from app.models.policy import Policy
from app.models.audit import AIFinding, AuditLog
from app.models.user import User, Department

dashboard_bp = Blueprint('dashboard', __name__)

@dashboard_bp.route('', methods=['GET'])
@jwt_required()
def get_analytics():
    # 1. Core KPIs
    total_contracts = Contract.query.count()
    total_policies = Policy.query.count()
    pending_reviews = Contract.query.filter_by(status='Pending Review').count()
    
    # Calculate average compliance score across analyzed versions
    latest_versions = db.session.query(
        ContractVersion.id
    ).join(
        Contract, Contract.id == ContractVersion.contract_id
    ).filter(
        Contract.current_version == ContractVersion.version_number
    ).all()
    
    latest_version_ids = [v[0] for v in latest_versions]
    
    high_risk_contracts = 0
    total_score = 0
    scores_count = 0
    
    if latest_version_ids:
        # Check high risk contracts
        high_risk_contracts = db.session.query(
            ContractVersion.contract_id
        ).join(
            AIFinding, AIFinding.version_id == ContractVersion.id
        ).filter(
            ContractVersion.id.in_(latest_version_ids),
            AIFinding.risk_level == 'High'
        ).distinct().count()
        
        # Calculate score for each contract
        for v_id in latest_version_ids:
            findings = AIFinding.query.filter_by(version_id=v_id).all()
            high_count = sum(1 for f in findings if f.risk_level == 'High')
            med_count = sum(1 for f in findings if f.risk_level == 'Medium')
            low_count = sum(1 for f in findings if f.risk_level == 'Low')
            
            score = 100 - (high_count * 15 + med_count * 5 + low_count * 1)
            score = max(0, min(100, score))
            total_score += score
            scores_count += 1
            
    avg_compliance_score = int(total_score / scores_count) if scores_count > 0 else 100

    # 2. Risk Distribution Chart
    # Group findings by category
    categories_data = db.session.query(
        AIFinding.category, func.count(AIFinding.id)
    ).group_by(
        AIFinding.category
    ).all()
    
    risk_distribution = [{"name": cat or "General", "value": count} for cat, count in categories_data]
    if not risk_distribution:
        risk_distribution = [
            {"name": "GDPR Violation", "value": 0},
            {"name": "Security Risk", "value": 0},
            {"name": "Payment Term", "value": 0},
            {"name": "Liability Issue", "value": 0},
            {"name": "Confidentiality", "value": 0}
        ]

    # 3. Monthly Uploads Chart Data (Simulated/Calculated)
    monthly_uploads = [
        {"month": "Jan", "contracts": 12, "policies": 2},
        {"month": "Feb", "contracts": 15, "policies": 1},
        {"month": "Mar", "contracts": 18, "policies": 3},
        {"month": "Apr", "contracts": 22, "policies": 1},
        {"month": "May", "contracts": 30, "policies": 4},
        {"month": "Jun", "contracts": total_contracts + 10, "policies": total_policies + 1}
    ]

    # 4. AI Token & Cost Usage Stats (Simulated)
    # Estimate based on contracts & findings
    estimated_tokens = (total_contracts * 8000) + (total_policies * 12000)
    estimated_cost = round(estimated_tokens * 0.000002, 2) # $0.002 per 1k tokens standard cost

    # 5. Recent Activity Feed
    recent_logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(10).all()
    
    return jsonify({
        "kpis": {
            "total_contracts": total_contracts,
            "total_policies": total_policies,
            "compliance_score": avg_compliance_score,
            "high_risk_contracts": high_risk_contracts,
            "pending_reviews": pending_reviews
        },
        "risk_distribution": risk_distribution,
        "monthly_uploads": monthly_uploads,
        "ai_usage": {
            "tokens_consumed": estimated_tokens,
            "api_calls": total_contracts + total_policies,
            "estimated_cost_usd": estimated_cost
        },
        "recent_activities": [log.to_dict() for log in recent_logs]
    }), 200
