from app.core.database import db
from app.models.audit import AuditLog
from app.utils.logger import rag_logger


def log_audit(user_id: str, action: str, details: str, ip_address: str = "System"):
    """
    Create a new entry in the audit_logs table.
    """
    try:
        log = AuditLog(
            user_id=user_id, action=action, ip_address=ip_address, details=details
        )
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        rag_logger.error(f"Error logging audit: {e}", exc_info=True)
