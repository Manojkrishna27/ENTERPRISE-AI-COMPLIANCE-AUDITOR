from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Request,
    UploadFile,
    status,
)
from sqlalchemy.orm import Session
from werkzeug.utils import secure_filename

from app.core.database import get_db
from app.core.dependencies import get_current_user, role_required
from app.models.policy import Policy, PolicyChunk
from app.models.user import User
from app.services.document_parser import DocumentParser
from app.services.qdrant_service import qdrant_service
from app.services.s3_service import storage_service
from app.utils.security import log_audit

router = APIRouter(prefix="/api/policies", tags=["Policies"])

ALLOWED_EXTENSIONS = {"pdf", "docx"}


def allowed_file(filename: str) -> bool:
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@router.get(
    "",
    summary="List all policies",
    description="Fetch list of compliance policies filtered by category",
)
def list_policies(
    category: str | None = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    query = db.query(Policy)
    if category:
        query = query.filter(Policy.category == category)
    policies = query.order_by(Policy.created_at.desc()).all()
    return [p.to_dict() for p in policies]


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    summary="Upload a new policy",
    description="Upload policy document and index chunks into vector database",
)
async def upload_policy(
    request: Request,
    file: UploadFile = File(...),
    name: str = Form(...),
    description: str | None = Form(""),
    category: str | None = Form("Custom"),
    current_user: User = Depends(role_required("Admin", "Compliance Officer")),
    db: Session = Depends(get_db),
):
    if not file or not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="No file selected"
        )

    if not name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Policy name is required"
        )

    if not allowed_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type. Only PDF and DOCX are allowed.",
        )

    file_ext = file.filename.rsplit(".", 1)[1].lower()
    filename = secure_filename(file.filename)

    policy = Policy(
        name=name,
        description=description or "",
        category=category or "Custom",
        s3_key="",
        file_type=file_ext.upper(),
        is_active=True,
    )
    db.add(policy)
    db.flush()

    s3_key = f"policies/{policy.id}_{filename}"
    policy.s3_key = s3_key

    try:
        contents = await file.read()
        storage_service.upload_file(contents, s3_key)

        local_path = storage_service.get_file_path(s3_key)
        parsed_chunks = DocumentParser.parse_document(local_path, file_ext)

        db_chunks = []
        for c in parsed_chunks:
            chunk = PolicyChunk(
                policy_id=policy.id,
                chunk_text=c["text"],
                page_number=c["page_number"],
                paragraph_number=c["paragraph_number"],
                chunk_position=c["chunk_position"],
            )
            db_chunks.append(chunk)
            db.add(chunk)

        db.flush()

        # Index policy chunks in Qdrant Vector Store
        qdrant_service.index_policy_chunks(policy.id, db_chunks)

        db.commit()

        client_ip = request.client.host if request.client else "System"
        log_audit(
            current_user.id,
            "POLICY_UPLOAD",
            f"Uploaded and indexed policy: {name}",
            ip_address=client_ip,
        )

        return {
            "msg": "Policy uploaded and indexed successfully",
            "policy": policy.to_dict(),
            "chunks_count": len(db_chunks),
        }
    except Exception as e:
        policy_id = policy.id if policy else None
        db.rollback()
        if policy_id:
            try:
                qdrant_service.delete_policy_chunks(policy_id)
            except Exception as inner_e:
                print(f"Error deleting qdrant chunks during rollback: {inner_e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload and index policy: {e!s}",
        )


@router.delete(
    "/{id}",
    summary="Delete policy",
    description="Delete policy document, chunks, and vector index",
)
def delete_policy(
    id: str,
    request: Request,
    current_user: User = Depends(role_required("Admin", "Compliance Officer")),
    db: Session = Depends(get_db),
):
    policy = db.query(Policy).filter(Policy.id == id).first()
    if not policy:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Policy not found"
        )

    try:
        storage_service.delete_file(policy.s3_key)
        qdrant_service.delete_policy_chunks(policy.id)
        db.delete(policy)
        db.commit()

        client_ip = request.client.host if request.client else "System"
        log_audit(
            current_user.id,
            "POLICY_DELETE",
            f"Deleted policy: {policy.name}",
            ip_address=client_ip,
        )
        return {"msg": "Policy deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete policy: {e!s}",
        )
