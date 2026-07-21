from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database import db
from app.models.contract import ContractVersion, ContractChunk, Contract
from app.models.policy import Policy, PolicyChunk
from app.models.audit import AIFinding
from app.models.notification import Notification
from app.services.qdrant_service import qdrant_service
from app.services.rag_service import rag_service
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
        # Instead of looping all chunks, we use RAG to find the most risky clauses
        compliance_query = "Compliance risks, GDPR, security requirements, liability limits, missing clauses, financial risks, privacy"
        
        matching_contract_chunks = qdrant_service.search_contract_chunks(version.id, compliance_query, limit=15)
        matching_policies = qdrant_service.search_policy_chunks(compliance_query, limit=10, department_id=contract.department_id)
        
        # Run LLM structured auditing
        analysis_result = rag_service.analyze_contract_compliance(
            contract_name=contract.name,
            contract_chunks=matching_contract_chunks,
            policy_chunks=matching_policies
        )
        
        # Parse new JSON format
        raw_findings = analysis_result.get("findings", [])
        
        # Save findings
        for f in raw_findings:
            contract_citation = f.get("contract_citation", {})
            policy_citation = f.get("policy_citation", {})
            
            finding = AIFinding(
                version_id=version.id,
                category=f.get('category', 'Compliance Issue'),
                risk_level=f.get('severity', 'Low'),
                title=f.get('title', 'Discrepancy'),
                explanation=f.get('description', ''),
                business_impact=f.get('business_impact', ''),
                recommendation=f.get('recommendation', ''),
                confidence_score=f.get('confidence', 1.0),
                contract_page_number=contract_citation.get("page", 1),
                contract_paragraph_number=contract_citation.get("paragraph", 1),
                policy_page_number=policy_citation.get("page"),
                policy_paragraph_number=policy_citation.get("paragraph"),
                matching_clause_text=f.get('matching_clause_text', ''),
                matching_policy_text=f.get('matching_policy_text', '')
            )
            
            if f.get('severity', '').upper() == 'HIGH':
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
            "compliance_score": analysis_result.get("compliance_score", 100),
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
    """
    RAG Copilot Chat
    ---
    tags:
      - Copilot
    security:
      - Bearer: []
    parameters:
      - in: path
        name: contract_id
        required: true
        type: string
      - in: path
        name: ver_id
        required: true
        type: string
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            question:
              type: string
    responses:
      200:
        description: AI generated response
    """
    limiter = current_app.extensions['limiter']
    limiter.limit("30 per minute")(lambda: None)()
    
    data = request.get_json() or {}
    question = data.get('question')
    
    if not question:
        return jsonify({"msg": "Question is required"}), 400
        
    print(f"\n--- RAG Copilot Request ---")
    print(f"Question: {question}")
        
    # Fetch contract context
    contract = Contract.query.get(contract_id)
    if not contract:
        return jsonify({"msg": "Contract not found"}), 404
        
    chunks = ContractChunk.query.filter_by(version_id=ver_id).order_by(ContractChunk.chunk_position.asc()).all()
    if not chunks:
        return jsonify({"msg": "No content found for this contract version"}), 400
        
    # Fallback on-the-fly indexing for legacy unindexed contracts
    unindexed_chunks = [c for c in chunks if not c.qdrant_id]
    if unindexed_chunks:
        print(f"Found {len(unindexed_chunks)} unindexed contract chunks. Indexing on-the-fly...")
        qdrant_service.index_contract_chunks(ver_id, unindexed_chunks)
        db.session.commit()
    
    try:
        # Retrieve matching contract and policy context using semantic query
        matching_contract_chunks = qdrant_service.search_contract_chunks(ver_id, question, limit=5)
        matching_policies = qdrant_service.search_policy_chunks(question, limit=5, department_id=contract.department_id)
        
        # Execute AI prompt completion
        response_data = rag_service.copilot_answer(
            query=question,
            contract_name=contract.name,
            contract_chunks=matching_contract_chunks,
            policy_chunks=matching_policies,
            retrieval_metrics={
                "retrieved_contract_chunks": len(matching_contract_chunks),
                "retrieved_policy_chunks": len(matching_policies)
            }
        )
        
        return jsonify({
            "question": question,
            "answer": response_data["content"],
            "metrics": {
                "prompt_tokens": response_data.get("prompt_tokens"),
                "completion_tokens": response_data.get("completion_tokens"),
                "latency_seconds": round(response_data.get("latency", 0), 2),
                "model_used": response_data.get("model"),
                "retrieved_contract": response_data.get("retrieved_contract_chunks"),
                "retrieved_policy": response_data.get("retrieved_policy_chunks")
            }
        }), 200
        
    except Exception as e:
        print(f"RAG Failure: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            "status": "error",
            "message": "RAG retrieval or LLM generation failed.",
            "details": str(e)
        }), 500
