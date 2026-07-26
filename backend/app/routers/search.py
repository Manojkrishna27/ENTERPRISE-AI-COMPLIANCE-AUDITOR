from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.models.contract import Contract
from app.models.policy import Policy
from app.models.user import User
from app.services.qdrant_service import qdrant_service

router = APIRouter(prefix="/api/search", tags=["Search"])


@router.get(
    "",
    summary="Global keyword & semantic search",
    description="Perform hybrid SQL keyword and vector semantic search across contracts and policies",
)
def search(
    q: str = Query("", alias="q"),
    type: str = Query("all", alias="type"),
    department_id: str | None = Query(None, alias="department_id"),
    risk_level: str | None = Query(None, alias="risk_level"),
    category: str | None = Query(None, alias="category"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query_str = q.strip()
    search_type = type.lower()

    results = {"contracts": [], "policies": [], "semantic_policy_matches": []}

    if not query_str:
        return results

    # 1. SQL Keyword search across Contracts (Name & Description)
    if search_type in ["all", "contracts"]:
        c_query = db.query(Contract).filter(
            (Contract.name.ilike(f"%{query_str}%"))
            | (Contract.description.ilike(f"%{query_str}%"))
        )
        if department_id:
            c_query = c_query.filter(Contract.department_id == department_id)
        if risk_level:
            c_query = c_query.filter(Contract.status == risk_level)

        contracts = c_query.limit(10).all()
        results["contracts"] = [c.to_dict() for c in contracts]

    # 2. SQL Keyword search across Policies (Name & Description)
    if search_type in ["all", "policies"]:
        p_query = db.query(Policy).filter(
            (Policy.name.ilike(f"%{query_str}%"))
            | (Policy.description.ilike(f"%{query_str}%"))
        )
        if category:
            p_query = p_query.filter(Policy.category == category)

        policies = p_query.limit(10).all()
        results["policies"] = [p.to_dict() for p in policies]

    # 3. Vector Semantic search in Qdrant across policies
    if search_type in ["all", "policies"]:
        try:
            semantic_matches = qdrant_service.search_policy_chunks(query_str, limit=5)

            enriched_matches = []
            for match in semantic_matches:
                p_id = match.get("policy_id")
                policy = (
                    db.query(Policy).filter(Policy.id == p_id).first() if p_id else None
                )
                if policy:
                    match["policy_name"] = policy.name
                    match["policy_category"] = policy.category
                enriched_matches.append(match)

            results["semantic_policy_matches"] = enriched_matches
        except Exception as e:
            print(f"Error fetching semantic matches in search API: {e}")
            results["semantic_policy_matches"] = []

    return results
