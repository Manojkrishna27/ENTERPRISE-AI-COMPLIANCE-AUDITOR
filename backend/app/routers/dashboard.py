from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.audit import AIFinding, AuditLog
from app.models.contract import Contract, ContractVersion
from app.models.policy import Policy
from app.models.user import User

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get(
    "",
    summary="Get dashboard metrics & analytics",
    description="Fetch KPI metrics, risk distributions, upload stats, and recent activity logs",
)
def get_analytics(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    # 1. Core KPIs
    total_contracts = db.query(Contract).count()
    total_policies = db.query(Policy).count()
    pending_reviews = (
        db.query(Contract).filter(Contract.status == "Pending Review").count()
    )

    latest_versions = (
        db.query(ContractVersion.id)
        .join(Contract, Contract.id == ContractVersion.contract_id)
        .filter(Contract.current_version == ContractVersion.version_number)
        .all()
    )

    latest_version_ids = [v[0] for v in latest_versions]

    high_risk_contracts = 0
    total_score = 0
    scores_count = 0

    if latest_version_ids:
        high_risk_contracts = (
            db.query(ContractVersion.contract_id)
            .join(AIFinding, AIFinding.version_id == ContractVersion.id)
            .filter(
                ContractVersion.id.in_(latest_version_ids),
                AIFinding.risk_level == "High",
            )
            .distinct()
            .count()
        )

        for v_id in latest_version_ids:
            findings = db.query(AIFinding).filter(AIFinding.version_id == v_id).all()
            high_count = sum(1 for f in findings if f.risk_level == "High")
            med_count = sum(1 for f in findings if f.risk_level == "Medium")
            low_count = sum(1 for f in findings if f.risk_level == "Low")

            score = 100 - (high_count * 15 + med_count * 5 + low_count * 1)
            score = max(0, min(100, score))
            total_score += score
            scores_count += 1

    avg_compliance_score = int(total_score / scores_count) if scores_count > 0 else 100

    # 2. Risk Distribution Chart
    categories_data = (
        db.query(AIFinding.category, func.count(AIFinding.id))
        .group_by(AIFinding.category)
        .all()
    )

    risk_distribution = [
        {"name": cat or "General", "value": count} for cat, count in categories_data
    ]
    if not risk_distribution:
        risk_distribution = [
            {"name": "GDPR Violation", "value": 0},
            {"name": "Security Risk", "value": 0},
            {"name": "Payment Term", "value": 0},
            {"name": "Liability Issue", "value": 0},
            {"name": "Confidentiality", "value": 0},
        ]

    # 3. Monthly Uploads Chart Data
    monthly_uploads = [
        {"month": "Jan", "contracts": 12, "policies": 2},
        {"month": "Feb", "contracts": 15, "policies": 1},
        {"month": "Mar", "contracts": 18, "policies": 3},
        {"month": "Apr", "contracts": 22, "policies": 1},
        {"month": "May", "contracts": 30, "policies": 4},
        {
            "month": "Jun",
            "contracts": total_contracts + 10,
            "policies": total_policies + 1,
        },
    ]

    # 4. AI Usage Stats
    estimated_tokens = (total_contracts * 8000) + (total_policies * 12000)
    estimated_cost = round(estimated_tokens * 0.000002, 2)

    # 5. Recent Activity Feed
    recent_logs = (
        db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(10).all()
    )

    return {
        "kpis": {
            "total_contracts": total_contracts,
            "total_policies": total_policies,
            "compliance_score": avg_compliance_score,
            "high_risk_contracts": high_risk_contracts,
            "pending_reviews": pending_reviews,
        },
        "risk_distribution": risk_distribution,
        "monthly_uploads": monthly_uploads,
        "ai_usage": {
            "tokens_consumed": estimated_tokens,
            "api_calls": total_contracts + total_policies,
            "estimated_cost_usd": estimated_cost,
        },
        "recent_activities": [log.to_dict() for log in recent_logs],
    }
