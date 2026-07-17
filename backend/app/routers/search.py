from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.database import db
from app.models.contract import Contract, ContractChunk, ContractVersion
from app.models.policy import Policy, PolicyChunk
from app.services.qdrant_service import qdrant_service

search_bp = Blueprint('search', __name__)

@search_bp.route('', methods=['GET'])
@jwt_required()
def search():
    query_str = request.args.get('q', '').strip()
    search_type = request.args.get('type', 'all')  # all, contracts, policies
    dept_id = request.args.get('department_id')
    risk_level = request.args.get('risk_level')
    category = request.args.get('category')  # policy category

    results = {
        "contracts": [],
        "policies": [],
        "semantic_policy_matches": []
    }

    if not query_str:
        return jsonify(results), 200

    # 1. SQL Keyword search across Contracts (Name & Description)
    if search_type in ['all', 'contracts']:
        c_query = Contract.query.filter(
            (Contract.name.ilike(f"%{query_str}%")) | 
            (Contract.description.ilike(f"%{query_str}%"))
        )
        if dept_id:
            c_query = c_query.filter_by(department_id=dept_id)
        if risk_level:
            c_query = c_query.filter_by(status=risk_level) # statuses like Draft, Pending, Approved
            
        contracts = c_query.limit(10).all()
        results["contracts"] = [c.to_dict() for c in contracts]

    # 2. SQL Keyword search across Policies (Name & Description)
    if search_type in ['all', 'policies']:
        p_query = Policy.query.filter(
            (Policy.name.ilike(f"%{query_str}%")) | 
            (Policy.description.ilike(f"%{query_str}%"))
        )
        if category:
            p_query = p_query.filter_by(category=category)
            
        policies = p_query.limit(10).all()
        results["policies"] = [p.to_dict() for p in policies]

    # 3. Vector Semantic search in Qdrant across policies
    if search_type in ['all', 'policies']:
        try:
            semantic_matches = qdrant_service.search_policy_chunks(query_str, limit=5)
            
            # Enrich semantic results with policy name details
            enriched_matches = []
            for match in semantic_matches:
                p_id = match.get('policy_id')
                policy = Policy.query.get(p_id) if p_id else None
                if policy:
                    match['policy_name'] = policy.name
                    match['policy_category'] = policy.category
                enriched_matches.append(match)
                
            results["semantic_policy_matches"] = enriched_matches
        except Exception as e:
            print(f"Error fetching semantic matches in search API: {e}")
            results["semantic_policy_matches"] = []

    return jsonify(results), 200
