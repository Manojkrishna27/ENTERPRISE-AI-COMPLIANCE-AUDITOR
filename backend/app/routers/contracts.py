import os
import uuid
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app.database import db
from app.models.contract import Contract, ContractVersion, ContractChunk
from app.models.user import User
from app.services.s3_service import storage_service
from app.services.document_parser import DocumentParser
from app.utils.security import role_required, log_audit

contracts_bp = Blueprint('contracts', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@contracts_bp.route('', methods=['GET'])
@jwt_required()
def list_contracts():
    dept_id = request.args.get('department_id')
    status = request.args.get('status')
    
    query = Contract.query
    if dept_id:
        query = query.filter_by(department_id=dept_id)
    if status:
        query = query.filter_by(status=status)
        
    contracts = query.order_by(Contract.updated_at.desc()).all()
    return jsonify([c.to_dict() for c in contracts]), 200


@contracts_bp.route('', methods=['POST'])
@jwt_required()
@role_required('Admin', 'Compliance Officer', 'Legal Reviewer', 'Auditor')
def upload_contract():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    # Validate file presence
    if 'file' not in request.files:
        return jsonify({"msg": "No file part in the request"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"msg": "No file selected"}), 400

    name = request.form.get('name')
    description = request.form.get('description', '')
    department_id = request.form.get('department_id', user.department_id)

    if not name:
        return jsonify({"msg": "Contract name is required"}), 400

    if not allowed_file(file.filename):
        return jsonify({"msg": "Unsupported file type. Only PDF and DOCX are allowed."}), 400

    file_ext = file.filename.rsplit('.', 1)[1].lower()
    
    # Save contract header
    contract = Contract(
        name=name,
        description=description,
        department_id=department_id,
        owner_id=user_id,
        status='Draft',
        current_version=1
    )
    db.session.add(contract)
    db.session.flush() # Generate contract ID
    
    # S3 Key structure: contracts/<contract_id>/v1_<filename>
    filename = secure_filename(file.filename)
    s3_key = f"contracts/{contract.id}/v1_{filename}"
    
    try:
        # Upload using storage service (local filesystem fallback or AWS S3)
        storage_service.upload_file(file, s3_key)
        
        # Save version header
        version = ContractVersion(
            contract_id=contract.id,
            version_number=1,
            s3_key=s3_key,
            file_type=file_ext.upper(),
            status='Processing'
        )
        db.session.add(version)
        db.session.flush() # Generate version ID
        
        # Parse document to chunks
        local_path = storage_service.get_file_path(s3_key)
        parsed_chunks = DocumentParser.parse_document(local_path, file_ext)
        
        # Save parsed chunks to SQL
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
            db.session.add(chunk)
            
        version.status = 'Uploaded'
        db.session.commit()
        
        log_audit(user_id, "CONTRACT_UPLOAD", f"Uploaded contract: {name} (Version 1)")
        
        return jsonify({
            "msg": "Contract uploaded and parsed successfully",
            "contract": contract.to_dict(),
            "version": version.to_dict(),
            "chunks_count": len(db_chunks)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error uploading/parsing contract: {e}")
        return jsonify({"msg": "Failed to process uploaded file", "error": str(e)}), 500


@contracts_bp.route('/<id>', methods=['GET'])
@jwt_required()
def get_contract(id):
    contract = Contract.query.get(id)
    if not contract:
        return jsonify({"msg": "Contract not found"}), 404
        
    versions = ContractVersion.query.filter_by(contract_id=id).order_by(ContractVersion.version_number.desc()).all()
    
    contract_data = contract.to_dict()
    contract_data['versions'] = [v.to_dict() for v in versions]
    return jsonify(contract_data), 200


@contracts_bp.route('/<id>/versions/<ver_id>', methods=['GET'])
@jwt_required()
def get_version(id, ver_id):
    version = ContractVersion.query.filter_by(id=ver_id, contract_id=id).first()
    if not version:
        return jsonify({"msg": "Contract version not found"}), 404
        
    chunks = ContractChunk.query.filter_by(version_id=ver_id).order_by(ContractChunk.chunk_position.asc()).all()
    
    version_data = version.to_dict()
    version_data['chunks'] = [c.to_dict() for c in chunks]
    return jsonify(version_data), 200


@contracts_bp.route('/<id>/versions', methods=['POST'])
@jwt_required()
@role_required('Admin', 'Compliance Officer', 'Legal Reviewer', 'Auditor')
def upload_version(id):
    contract = Contract.query.get(id)
    if not contract:
        return jsonify({"msg": "Contract not found"}), 404
        
    if 'file' not in request.files:
        return jsonify({"msg": "No file part in the request"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"msg": "No file selected"}), 400

    if not allowed_file(file.filename):
        return jsonify({"msg": "Unsupported file type. Only PDF and DOCX are allowed."}), 400

    file_ext = file.filename.rsplit('.', 1)[1].lower()
    
    user_id = get_jwt_identity()
    new_version_num = contract.current_version + 1
    filename = secure_filename(file.filename)
    s3_key = f"contracts/{contract.id}/v{new_version_num}_{filename}"
    
    try:
        # Upload
        storage_service.upload_file(file, s3_key)
        
        # Save version header
        version = ContractVersion(
            contract_id=contract.id,
            version_number=new_version_num,
            s3_key=s3_key,
            file_type=file_ext.upper(),
            status='Processing'
        )
        db.session.add(version)
        
        # Parse chunks
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
            db.session.add(chunk)
            
        # Update contract current version
        contract.current_version = new_version_num
        version.status = 'Uploaded'
        db.session.commit()
        
        log_audit(user_id, "CONTRACT_VERSION_UPLOAD", f"Uploaded version {new_version_num} for contract: {contract.name}")
        
        return jsonify({
            "msg": "New contract version uploaded successfully",
            "contract": contract.to_dict(),
            "version": version.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        print(f"Error uploading version: {e}")
        return jsonify({"msg": "Failed to upload version", "error": str(e)}), 500


@contracts_bp.route('/<id>', methods=['DELETE'])
@jwt_required()
@role_required('Admin', 'Compliance Officer')
def delete_contract(id):
    contract = Contract.query.get(id)
    if not contract:
        return jsonify({"msg": "Contract not found"}), 404
        
    user_id = get_jwt_identity()
    
    # Delete associated files from storage first
    for version in contract.versions:
        try:
            storage_service.delete_file(version.s3_key)
        except Exception as e:
            print(f"Failed to delete file {version.s3_key}: {e}")
            
    db.session.delete(contract)
    db.session.commit()
    
    log_audit(user_id, "CONTRACT_DELETE", f"Deleted contract: {contract.name}")
    return jsonify({"msg": "Contract and all versions deleted successfully"}), 200


@contracts_bp.route('/<id>/archive', methods=['POST'])
@jwt_required()
@role_required('Admin', 'Compliance Officer', 'Legal Reviewer')
def archive_contract(id):
    contract = Contract.query.get(id)
    if not contract:
        return jsonify({"msg": "Contract not found"}), 404
        
    user_id = get_jwt_identity()
    contract.status = 'Archived'
    db.session.commit()
    
    log_audit(user_id, "CONTRACT_ARCHIVE", f"Archived contract: {contract.name}")
    return jsonify({"msg": "Contract archived successfully", "contract": contract.to_dict()}), 200


@contracts_bp.route('/<id>/restore', methods=['POST'])
@jwt_required()
@role_required('Admin', 'Compliance Officer', 'Legal Reviewer')
def restore_contract(id):
    contract = Contract.query.get(id)
    if not contract:
        return jsonify({"msg": "Contract not found"}), 404
        
    user_id = get_jwt_identity()
    contract.status = 'Draft'
    db.session.commit()
    
    log_audit(user_id, "CONTRACT_RESTORE", f"Restored contract: {contract.name}")
    return jsonify({"msg": "Contract restored to Draft status", "contract": contract.to_dict()}), 200
