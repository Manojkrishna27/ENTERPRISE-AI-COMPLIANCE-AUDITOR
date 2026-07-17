from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database import db
from app.models.contract import ContractVersion, ContractChunk, Contract
from app.models.policy import Policy, PolicyChunk
from app.models.audit import AIFinding
from app.models.notification import Notification
from app.services.qdrant_service import qdrant_service
from app.services.openai_service import openai_service
from app.utils.security import role_required, log_audit

analysis_bp = Blueprint('analysis', __name__)

@analysis_bp.route('/contracts/<contract_id>/version/<ver_id>/analyze', methods=['POST'])
@jwt_required()
@role_required('Admin', 'Compliance Officer', 'Legal Reviewer', 'Auditor')
def run_analysis(contract_id, ver_id):
    user_id = get_jwt_identity()
    
    # Verify version and contract
    version = ContractVersion.query.filter_by(id=ver_id, contract_id=contract_id).first()
    if not version:
        return jsonify({"msg": "Contract version not found"}), 404
        
    contract = Contract.query.get(contract_id)
    
    # Clear existing findings for this version to avoid duplicates on re-analysis
    AIFinding.query.filter_by(version_id=ver_id).delete()
    
    # Retrieve all text chunks of this contract version
    chunks = ContractChunk.query.filter_by(version_id=ver_id).order_by(ContractChunk.chunk_position.asc()).all()
    if not chunks:
        return jsonify({"msg": "No text chunks found for this contract version. Verify if parsed correctly."}), 400
        
    version.status = 'Analyzing'
    db.session.commit()
    
    findings_count = 0
    high_risk_detected = False
    
    try:
        # Loop through chunks and search Qdrant for policy matches
        for chunk in chunks:
            # Query Qdrant for relevant policies
            matching_policies = qdrant_service.search_policy_chunks(chunk.chunk_text, limit=2)
            
            # Run LLM structured auditing
            raw_findings = openai_service.analyze_clause_against_policy(
                contract_chunk_text=chunk.chunk_text,
                contract_page=chunk.page_number,
                contract_para=chunk.paragraph_number,
                policy_chunks=matching_policies
            )
            
            # Save findings returned from OpenAI
            for f in raw_findings:
                # Resolve policy ID if matched
                p_id = f.get('policy_id')
                if p_id:
                    # Double check policy exists in SQL
                    sql_policy = Policy.query.get(p_id)
                    if not sql_policy:
                        p_id = None
                
                finding = AIFinding(
                    version_id=version.id,
                    category=f.get('category', 'Custom'),
                    risk_level=f.get('risk_level', 'Low'),
                    title=f.get('title', 'Compliance Discrepancy'),
                    explanation=f.get('explanation', ''),
                    business_impact=f.get('business_impact', ''),
                    recommendation=f.get('recommendation', ''),
                    confidence_score=f.get('confidence_score', 1.0),
                    contract_page_number=chunk.page_number,
                    contract_paragraph_number=chunk.paragraph_number,
                    policy_id=p_id,
                    policy_page_number=f.get('policy_page_number'),
                    policy_paragraph_number=f.get('policy_paragraph_number'),
                    matching_clause_text=f.get('matching_clause_text') or chunk.chunk_text[:300],
                    matching_policy_text=f.get('matching_policy_text')
                )
                
                if f.get('risk_level') == 'High':
                    high_risk_detected = True
                    
                db.session.add(finding)
                findings_count += 1
                
        # Update statuses
        version.status = 'Analyzed'
        contract.status = 'Pending Review'
        
        # Trigger system notification
        msg = f"Compliance analysis completed for contract '{contract.name}' (Version {version.version_number}). Detected {findings_count} findings."
        if high_risk_detected:
            msg += " WARNING: High risk issues were identified."
            
        notification = Notification(
            user_id=user_id,
            message=msg,
            notification_type='High Risk' if high_risk_detected else 'Analysis Complete'
        )
        db.session.add(notification)
        
        db.session.commit()
        log_audit(user_id, "CONTRACT_ANALYZE", f"Analyzed contract: {contract.name} (V{version.version_number})")
        
        return jsonify({
            "msg": "Analysis completed successfully",
            "findings_count": findings_count,
            "status": "Analyzed",
            "high_risk_detected": high_risk_detected
        }), 200
        
    except Exception as e:
        db.session.rollback()
        version.status = 'Error'
        db.session.commit()
        print(f"Error during contract analysis: {e}")
        return jsonify({"msg": "Failed during compliance analysis run", "error": str(e)}), 500


@analysis_bp.route('/contracts/<contract_id>/version/<ver_id>/findings', methods=['GET'])
@jwt_required()
def get_findings(contract_id, ver_id):
    findings = AIFinding.query.filter_by(version_id=ver_id).order_by(AIFinding.risk_level.desc()).all()
    return jsonify([f.to_dict() for f in findings]), 200


@analysis_bp.route('/contracts/<contract_id>/version/<ver_id>/copilot', methods=['POST'])
@jwt_required()
def copilot_chat(contract_id, ver_id):
    data = request.get_json() or {}
    query = data.get('query')
    
    if not query:
        return jsonify({"msg": "Query is required"}), 400
        
    # Fetch contract context
    contract = Contract.query.get(contract_id)
    if not contract:
        return jsonify({"msg": "Contract not found"}), 404
        
    chunks = ContractChunk.query.filter_by(version_id=ver_id).order_by(ContractChunk.chunk_position.asc()).all()
    contract_chunks_list = [{"page_number": c.page_number, "paragraph_number": c.paragraph_number, "text": c.chunk_text} for c in chunks]
    
    # Retrieve matching policy context using semantic query
    matching_policies = qdrant_service.search_policy_chunks(query, limit=3)
    
    # Execute AI prompt completion
    response_text = openai_service.copilot_answer(
        query=query,
        contract_name=contract.name,
        contract_chunks=contract_chunks_list,
        policy_chunks=matching_policies
    )
    
    return jsonify({
        "query": query,
        "answer": response_text
    }), 200
