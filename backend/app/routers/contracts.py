import os
import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form, Request, BackgroundTasks
from sqlalchemy.orm import Session
from werkzeug.utils import secure_filename

from app.core.database import get_db
from app.core.dependencies import get_current_user, role_required
from app.models.contract import Contract, ContractVersion, ContractChunk
from app.models.user import User
from app.services.s3_service import storage_service
from app.services.document_parser import DocumentParser
from app.services.qdrant_service import qdrant_service
from app.utils.security import log_audit

router = APIRouter(prefix="/api/contracts", tags=["Contracts"])

ALLOWED_EXTENSIONS = {'pdf', 'docx'}

def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_and_index_contract(version_id: str, local_path: str, file_ext: str):
    """Background task to parse and index contract chunks into Qdrant."""
    db = get_db().__next__()
    try:
        version = db.query(ContractVersion).filter(ContractVersion.id == version_id).first()
        if not version:
            return
        parsed_chunks = DocumentParser.parse_document(local_path, file_ext)
        db_chunks = []
        for c in parsed_chunks:
            chunk = ContractChunk(
                version_id=version.id,
                chunk_text=c['text'],
                page_number=c['page_number'],
                paragraph_number=c['paragraph_number'],
                chunk_position=c['chunk_position']
            )
            db_chunks.append(chunk)
            db.add(chunk)
            
        version.status = 'Uploaded'
        db.commit()
        
        qdrant_service.index_contract_chunks(version.id, db_chunks)
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error in background indexing: {e}")
    finally:
        db.close()


@router.get("", summary="List all contracts", description="Fetch list of contracts filtered by department or status")
def list_contracts(
    department_id: Optional[str] = None,
    status: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    query = db.query(Contract)
    if department_id:
        query = query.filter(Contract.department_id == department_id)
    if status:
        query = query.filter(Contract.status == status)
        
    contracts = query.order_by(Contract.updated_at.desc()).all()
    return [c.to_dict() for c in contracts]


@router.post("", status_code=status.HTTP_201_CREATED, summary="Upload a new contract", description="Upload contract file (PDF/DOCX) and store headers and version details")
async def upload_contract(
    request: Request,
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    name: str = Form(...),
    description: Optional[str] = Form(""),
    department_id: Optional[str] = Form(None),
    current_user: User = Depends(role_required('Admin', 'Compliance Officer', 'Legal Reviewer', 'Auditor')),
    db: Session = Depends(get_db)
):
    if not file or not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file selected")

    if not name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Contract name is required")

    if not allowed_file(file.filename):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type. Only PDF and DOCX are allowed.")

    dept_id = department_id or current_user.department_id
    file_ext = file.filename.rsplit('.', 1)[1].lower()
    filename = secure_filename(file.filename)

    contract = Contract(
        name=name,
        description=description or "",
        department_id=dept_id,
        owner_id=current_user.id,
        status='Draft',
        current_version=1
    )
    db.add(contract)
    db.flush()

    s3_key = f"contracts/{contract.id}/v1_{filename}"

    try:
        contents = await file.read()
        storage_service.upload_file(contents, s3_key)

        version = ContractVersion(
            contract_id=contract.id,
            version_number=1,
            s3_key=s3_key,
            file_type=file_ext.upper(),
            status='Processing'
        )
        db.add(version)
        db.flush()

        local_path = storage_service.get_file_path(s3_key)
        parsed_chunks = DocumentParser.parse_document(local_path, file_ext)

        db_chunks = []
        for c in parsed_chunks:
            chunk = ContractChunk(
                version_id=version.id,
                chunk_text=c['text'],
                page_number=c['page_number'],
                paragraph_number=c['paragraph_number'],
                chunk_position=c['chunk_position']
            )
            db_chunks.append(chunk)
            db.add(chunk)

        version.status = 'Uploaded'
        db.commit()

        # Vector Indexing
        qdrant_service.index_contract_chunks(version.id, db_chunks)
        db.commit()

        client_ip = request.client.host if request.client else "System"
        log_audit(current_user.id, "CONTRACT_UPLOAD", f"Uploaded contract: {name} (Version 1)", ip_address=client_ip)

        return {
            "msg": "Contract uploaded and parsed successfully",
            "contract": contract.to_dict(),
            "version": version.to_dict(),
            "chunks_count": len(db_chunks)
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to process uploaded file: {str(e)}")


@router.get("/{id}", summary="Get contract details", description="Fetch contract by ID with all versions")
def get_contract(
    id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    contract = db.query(Contract).filter(Contract.id == id).first()
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")

    versions = db.query(ContractVersion).filter(ContractVersion.contract_id == id).order_by(ContractVersion.version_number.desc()).all()

    contract_data = contract.to_dict()
    contract_data['versions'] = [v.to_dict() for v in versions]
    return contract_data


@router.get("/{id}/versions/{ver_id}", summary="Get contract version details", description="Fetch contract version and parsed text chunks")
def get_version(
    id: str,
    ver_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    version = db.query(ContractVersion).filter(ContractVersion.id == ver_id, ContractVersion.contract_id == id).first()
    if not version:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract version not found")

    chunks = db.query(ContractChunk).filter(ContractChunk.version_id == ver_id).order_by(ContractChunk.chunk_position.asc()).all()

    version_data = version.to_dict()
    version_data['chunks'] = [c.to_dict() for c in chunks]
    return version_data


@router.post("/{id}/versions", status_code=status.HTTP_201_CREATED, summary="Upload new contract version", description="Upload new version for an existing contract")
async def upload_version(
    id: str,
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(role_required('Admin', 'Compliance Officer', 'Legal Reviewer', 'Auditor')),
    db: Session = Depends(get_db)
):
    contract = db.query(Contract).filter(Contract.id == id).first()
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")

    if not file or not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No file selected")

    if not allowed_file(file.filename):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type. Only PDF and DOCX are allowed.")

    file_ext = file.filename.rsplit('.', 1)[1].lower()
    new_version_num = contract.current_version + 1
    filename = secure_filename(file.filename)
    s3_key = f"contracts/{contract.id}/v{new_version_num}_{filename}"

    try:
        contents = await file.read()
        storage_service.upload_file(contents, s3_key)

        version = ContractVersion(
            contract_id=contract.id,
            version_number=new_version_num,
            s3_key=s3_key,
            file_type=file_ext.upper(),
            status='Processing'
        )
        db.add(version)

        local_path = storage_service.get_file_path(s3_key)
        parsed_chunks = DocumentParser.parse_document(local_path, file_ext)

        for c in parsed_chunks:
            chunk = ContractChunk(
                version_id=version.id,
                chunk_text=c['text'],
                page_number=c['page_number'],
                paragraph_number=c['paragraph_number'],
                chunk_position=c['chunk_position']
            )
            db.add(chunk)

        contract.current_version = new_version_num
        version.status = 'Uploaded'
        db.commit()

        db_chunks = db.query(ContractChunk).filter(ContractChunk.version_id == version.id).all()
        qdrant_service.index_contract_chunks(version.id, db_chunks)
        db.commit()

        client_ip = request.client.host if request.client else "System"
        log_audit(current_user.id, "CONTRACT_VERSION_UPLOAD", f"Uploaded version {new_version_num} for contract: {contract.name}", ip_address=client_ip)

        return {
            "msg": "New contract version uploaded successfully",
            "contract": contract.to_dict(),
            "version": version.to_dict()
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to upload version: {str(e)}")


@router.delete("/{id}", summary="Delete contract", description="Delete contract and all associated versions & vector embeddings")
def delete_contract(
    id: str,
    request: Request,
    current_user: User = Depends(role_required('Admin', 'Compliance Officer')),
    db: Session = Depends(get_db)
):
    contract = db.query(Contract).filter(Contract.id == id).first()
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")

    for version in contract.versions:
        try:
            storage_service.delete_file(version.s3_key)
        except Exception as e:
            print(f"Failed to delete file {version.s3_key}: {e}")

    db.delete(contract)
    db.commit()

    client_ip = request.client.host if request.client else "System"
    log_audit(current_user.id, "CONTRACT_DELETE", f"Deleted contract: {contract.name}", ip_address=client_ip)
    return {"msg": "Contract and all versions deleted successfully"}


@router.post("/{id}/archive", summary="Archive contract", description="Change contract status to Archived")
def archive_contract(
    id: str,
    request: Request,
    current_user: User = Depends(role_required('Admin', 'Compliance Officer', 'Legal Reviewer')),
    db: Session = Depends(get_db)
):
    contract = db.query(Contract).filter(Contract.id == id).first()
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")

    contract.status = 'Archived'
    db.commit()

    client_ip = request.client.host if request.client else "System"
    log_audit(current_user.id, "CONTRACT_ARCHIVE", f"Archived contract: {contract.name}", ip_address=client_ip)
    return {"msg": "Contract archived successfully", "contract": contract.to_dict()}


@router.post("/{id}/restore", summary="Restore contract", description="Restore archived contract status back to Draft")
def restore_contract(
    id: str,
    request: Request,
    current_user: User = Depends(role_required('Admin', 'Compliance Officer', 'Legal Reviewer')),
    db: Session = Depends(get_db)
):
    contract = db.query(Contract).filter(Contract.id == id).first()
    if not contract:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Contract not found")

    contract.status = 'Draft'
    db.commit()

    client_ip = request.client.host if request.client else "System"
    log_audit(current_user.id, "CONTRACT_RESTORE", f"Restored contract: {contract.name}", ip_address=client_ip)
    return {"msg": "Contract restored to Draft status", "contract": contract.to_dict()}
