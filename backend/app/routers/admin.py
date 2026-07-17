from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.database import db
from app.models.user import User, Department
from app.models.audit import AuditLog
from app.utils.security import role_required, log_audit

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/users', methods=['GET'])
@jwt_required()
@role_required('Admin')
def list_users():
    users = User.query.order_by(User.created_at.desc()).all()
    return jsonify([u.to_dict() for u in users]), 200


@admin_bp.route('/users/<id>/role', methods=['PUT'])
@jwt_required()
@role_required('Admin')
def update_user_role(id):
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    new_role = data.get('role')
    
    if not new_role or new_role not in ['Admin', 'Compliance Officer', 'Legal Reviewer', 'Auditor', 'Viewer']:
        return jsonify({"msg": "Invalid or missing role"}), 400
        
    target_user = User.query.get(id)
    if not target_user:
        return jsonify({"msg": "User not found"}), 404
        
    old_role = target_user.role
    target_user.role = new_role
    db.session.commit()
    
    log_audit(user_id, "USER_ROLE_UPDATE", f"Updated user {target_user.email} role from {old_role} to {new_role}")
    return jsonify({"msg": "User role updated successfully", "user": target_user.to_dict()}), 200


@admin_bp.route('/departments', methods=['GET'])
@jwt_required()
def list_departments():
    depts = Department.query.order_by(Department.name.asc()).all()
    return jsonify([d.to_dict() for d in depts]), 200


@admin_bp.route('/departments', methods=['POST'])
@jwt_required()
@role_required('Admin')
def create_department():
    user_id = get_jwt_identity()
    data = request.get_json() or {}
    name = data.get('name')
    description = data.get('description', '')
    
    if not name:
        return jsonify({"msg": "Department name is required"}), 400
        
    if Department.query.filter_by(name=name).first():
        return jsonify({"msg": "Department with this name already exists"}), 409
        
    dept = Department(name=name, description=description)
    db.session.add(dept)
    db.session.commit()
    
    log_audit(user_id, "DEPARTMENT_CREATE", f"Created department: {name}")
    return jsonify({"msg": "Department created successfully", "department": dept.to_dict()}), 201


@admin_bp.route('/audit-logs', methods=['GET'])
@jwt_required()
@role_required('Admin', 'Compliance Officer')
def list_audit_logs():
    logs = AuditLog.query.order_by(AuditLog.created_at.desc()).limit(100).all()
    return jsonify([log.to_dict() for log in logs]), 200
