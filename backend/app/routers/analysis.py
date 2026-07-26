from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, role_required
from app.models.audit import AIFinding
from app.models.contract import Contract, ContractChunk, ContractVersion
from app.models.notification import Notification
from app.models.user import User
from app.schemas.analysis import CopilotChatSchema
from app.services.qdrant_service import qdrant_service
from app.services.rag_service import rag_service
from app.utils.security import log_audit

router = APIRouter(prefix="/api/analysis", tags=["Analysis & Copilot"])


@router.post(
    "/contracts/{contract_id}/version/{ver_id}/analyze",
    summary="Run compliance analysis",
    description="Perform AI RAG analysis against compliance guidelines",
)
def run_analysis(
    contract_id: str,
    ver_id: str,
    request: Request,
    current_user: User = Depends(
        role_required("Admin", "Compliance Officer", "Legal Reviewer", "Auditor")
    ),
    db: Session = Depends(get_db),
):
    version = (
        db.query(ContractVersion)
        .filter(
            ContractVersion.id == ver_id, ContractVersion.contract_id == contract_id
        )
        .first()
    )
    if not version:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contract version not found"
        )

    contract = db.query(Contract).filter(Contract.id == contract_id).first()

    # Clear existing findings to avoid duplicates
    db.query(AIFinding).filter(AIFinding.version_id == ver_id).delete()

    chunks = (
        db.query(ContractChunk)
        .filter(ContractChunk.version_id == ver_id)
        .order_by(ContractChunk.chunk_position.asc())
        .all()
    )
    if not chunks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No text chunks found for this contract version. Verify if parsed correctly.",
        )

    version.status = "Analyzing"
    db.commit()

    findings_count = 0
    high_risk_detected = False

    try:
        compliance_query = "Compliance risks, GDPR, security requirements, liability limits, missing clauses, financial risks, privacy"

        matching_contract_chunks = qdrant_service.search_contract_chunks(
            version.id, compliance_query, limit=15
        )
        matching_policies = qdrant_service.search_policy_chunks(
            compliance_query,
            limit=10,
            department_id=contract.department_id if contract else None,
        )

        analysis_result = rag_service.analyze_contract_compliance(
            contract_name=contract.name if contract else "Contract",
            contract_chunks=matching_contract_chunks,
            policy_chunks=matching_policies,
        )

        raw_findings = analysis_result.get("findings", [])

        for f in raw_findings:
            contract_citation = f.get("contract_citation") or {}
            policy_citation = f.get("policy_citation") or {}

            finding = AIFinding(
                version_id=version.id,
                category=f.get("category", "Compliance Issue"),
                risk_level=f.get("severity", "Low"),
                title=f.get("title", "Discrepancy"),
                explanation=f.get("description", ""),
                business_impact=f.get("business_impact", ""),
                recommendation=f.get("recommendation", ""),
                confidence_score=f.get("confidence", 1.0),
                contract_page_number=contract_citation.get("page", 1),
                contract_paragraph_number=contract_citation.get("paragraph", 1),
                policy_page_number=policy_citation.get("page"),
                policy_paragraph_number=policy_citation.get("paragraph"),
                matching_clause_text=f.get("matching_clause_text", ""),
                matching_policy_text=f.get("matching_policy_text", ""),
            )

            if f.get("severity", "").upper() == "HIGH":
                high_risk_detected = True

            db.add(finding)
            findings_count += 1

        version.status = "Analyzed"
        if contract:
            contract.status = "Pending Review"

        msg = f"Compliance analysis completed for contract '{contract.name if contract else ''}' (Version {version.version_number}). Detected {findings_count} findings."
        if high_risk_detected:
            msg += " WARNING: High risk issues were identified."

        notification = Notification(
            user_id=current_user.id,
            message=msg,
            notification_type=(
                "High Risk" if high_risk_detected else "Analysis Complete"
            ),
        )
        db.add(notification)

        db.commit()
        client_ip = request.client.host if request.client else "System"
        log_audit(
            current_user.id,
            "CONTRACT_ANALYZE",
            f"Analyzed contract: {contract.name if contract else ''} (V{version.version_number})",
            ip_address=client_ip,
        )

        return {
            "msg": "Analysis completed successfully",
            "findings_count": findings_count,
            "compliance_score": analysis_result.get("compliance_score", 100),
            "status": "Analyzed",
            "high_risk_detected": high_risk_detected,
        }
    except Exception as e:
        db.rollback()
        version.status = "Error"
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed during compliance analysis run: {e!s}",
        )


@router.get(
    "/contracts/{contract_id}/version/{ver_id}/findings",
    summary="Get contract findings",
    description="Fetch list of AI findings for contract version",
)
def get_findings(
    contract_id: str,
    ver_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    findings = (
        db.query(AIFinding)
        .filter(AIFinding.version_id == ver_id)
        .order_by(AIFinding.risk_level.desc())
        .all()
    )
    return [f.to_dict() for f in findings]


@router.post(
    "/contracts/{contract_id}/version/{ver_id}/copilot",
    summary="Copilot RAG Chat",
    description="Query AI Copilot with contract & policy context retrieval",
)
def copilot_chat(
    contract_id: str,
    ver_id: str,
    data: CopilotChatSchema,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    question = data.question
    if not question:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Question is required"
        )

    contract = db.query(Contract).filter(Contract.id == contract_id).first()
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found"
        )

    chunks = (
        db.query(ContractChunk)
        .filter(ContractChunk.version_id == ver_id)
        .order_by(ContractChunk.chunk_position.asc())
        .all()
    )
    if not chunks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No content found for this contract version",
        )

    unindexed_chunks = [c for c in chunks if not c.qdrant_id]
    if unindexed_chunks:
        qdrant_service.index_contract_chunks(ver_id, unindexed_chunks)
        db.commit()

    try:
        matching_contract_chunks = qdrant_service.search_contract_chunks(
            ver_id, question, limit=5
        )
        matching_policies = qdrant_service.search_policy_chunks(
            question, limit=5, department_id=contract.department_id
        )

        response_data = rag_service.copilot_answer(
            query=question,
            contract_name=contract.name,
            contract_chunks=matching_contract_chunks,
            policy_chunks=matching_policies,
            retrieval_metrics={
                "retrieved_contract_chunks": len(matching_contract_chunks),
                "retrieved_policy_chunks": len(matching_policies),
            },
        )

        metrics_dict = response_data.get("metrics", {})
        return {
            "question": question,
            "answer": response_data.get("answer") or response_data.get("content", ""),
            "metrics": {
                "prompt_tokens": metrics_dict.get("prompt_tokens", 0),
                "completion_tokens": metrics_dict.get("completion_tokens", 0),
                "latency_seconds": round(metrics_dict.get("latency", 0.0), 2),
                "model_used": metrics_dict.get("model", ""),
                "retrieved_contract": metrics_dict.get("contract_chunks", 0),
                "retrieved_policy": metrics_dict.get("policy_chunks", 0),
            },
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"RAG retrieval or LLM generation failed: {e!s}",
        )
