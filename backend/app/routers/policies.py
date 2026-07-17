from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app.database import db
from app.models.policy import Policy, PolicyChunk
from app.services.s3_service import storage_service
from app.services.document_parser import DocumentParser
from app.services.qdrant_service import qdrant_service
from app.utils.security import role_required, log_audit

policies_bp = Blueprint('policies', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@policies_bp.route('', methods=['GET'])
@jwt_required()
def list_policies():
    category = request.args.get('category')
    query = Policy.query
    if category:
        query = query.filter_by(category=category)
    policies = query.order_by(Policy.created_at.desc()).all()
    return jsonify([p.to_dict() for p in policies]), 200


@policies_bp.route('', methods=['POST'])
@jwt_required()
@role_required('Admin', 'Compliance Officer')
def upload_policy():
    user_id = get_jwt_identity()

    if 'file' not in request.files:
        return jsonify({"msg": "No file part in request"}), 400
        
    file = request.files['file']
    if file.filename == '':
        return jsonify({"msg": "No file selected"}), 400

    name = request.form.get('name')
    description = request.form.get('description', '')
    category = request.form.get('category', 'Custom') # GDPR, ISO27001, SOC2, Internal, Vendor, Custom

    if not name:
        return jsonify({"msg": "Policy name is required"}), 400

    if not allowed_file(file.filename):
        return jsonify({"msg": "Unsupported file type. Only PDF and DOCX are allowed."}), 400

    file_ext = file.filename.rsplit('.', 1)[1].lower()
    
    # Save Policy header
    policy = Policy(
        name=name,
        description=description,
        category=category,
        s3_key="",
        file_type=file_ext.upper(),
        is_active=True
    )
    db.session.add(policy)
    db.session.flush() # Generate ID
    
    filename = secure_filename(file.filename)
    s3_key = f"policies/{policy.id}_{filename}"
    policy.s3_key = s3_key
    
    try:
        # Save file
        storage_service.upload_file(file, s3_key)
        
        # Parse text chunks
        local_path = storage_service.get_file_path(s3_key)
        parsed_chunks = DocumentParser.parse_document(local_path, file_ext)
        
        db_chunks = []
        for c in parsed_chunks:
            chunk = PolicyChunk(
                policy_id=policy.id,
                chunk_text=c['text'],
                page_number=c['page_number'],
                paragraph_number=c['paragraph_number'],
                chunk_position=c['chunk_position']
            )
            db_chunks.append(chunk)
            db.session.add(chunk)
            
        db.session.flush() # Assign IDs to DB chunks
        
        # Index chunks in Qdrant Vector Store
        qdrant_service.index_policy_chunks(policy.id, db_chunks)
        
        db.session.commit()
        log_audit(user_id, "POLICY_UPLOAD", f"Uploaded and indexed policy: {name}")
        
        return jsonify({
            "msg": "Policy uploaded and indexed successfully",
            "policy": policy.to_dict(),
            "chunks_count": len(db_chunks)
        }), 201
        
    except Exception as e:
        db.session.rollback()
        # Clean up Qdrant index if failed
        qdrant_service.delete_policy_chunks(policy.id)
        print(f"Error processing policy: {e}")
        return jsonify({"msg": "Failed to upload and index policy", "error": str(e)}), 500


@policies_bp.route('/<id>', methods=['DELETE'])
@jwt_required()
@role_required('Admin', 'Compliance Officer')
def delete_policy(id):
    policy = Policy.query.get(id)
    if not policy:
        return jsonify({"msg": "Policy not found"}), 404
        
    user_id = get_jwt_identity()
    
    try:
        # Delete file from storage
        storage_service.delete_file(policy.s3_key)
        
        # Delete from Qdrant vector store
        qdrant_service.delete_policy_chunks(policy.id)
        
        # Delete policy database records
        db.session.delete(policy)
        db.session.commit()
        
        log_audit(user_id, "POLICY_DELETE", f"Deleted policy: {policy.name}")
        return jsonify({"msg": "Policy deleted successfully"}), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting policy: {e}")
        return jsonify({"msg": "Failed to delete policy", "error": str(e)}), 500
