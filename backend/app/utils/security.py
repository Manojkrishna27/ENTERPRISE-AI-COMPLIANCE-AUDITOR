from functools import wraps
from flask import request, jsonify
from flask_jwt_extended import verify_jwt_in_request, get_jwt
from app.database import db
from app.models.audit import AuditLog

def role_required(*roles):
    """
    Decorator to restrict access to users with specific roles.
    Must be placed after JWT verification.
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            claims = get_jwt()
            user_role = claims.get("role")
            
            if user_role not in roles:
                return jsonify({"msg": f"Access denied. Required roles: {', '.join(roles)}", "error": "forbidden"}), 403
            return fn(*args, **kwargs)
        return wrapper
    return decorator

def log_audit(user_id, action, details):
    """
    Create a new entry in the audit_logs table.
    """
    try:
        ip_address = request.remote_addr if request else "System"
        log = AuditLog(
            user_id=user_id,
            action=action,
            ip_address=ip_address,
            details=details
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        print(f"Error logging audit: {e}")
        # Rollback db session if it failed inside request context
        db.session.rollback()
