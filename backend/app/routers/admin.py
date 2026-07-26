from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user, role_required
from app.models.user import User, Department
from app.models.audit import AuditLog
from app.utils.security import log_audit
from app.schemas.auth import UserRoleUpdateSchema, DepartmentCreateSchema

router = APIRouter(prefix="/api/admin", tags=["Admin"])

@router.get("/users", summary="List all system users", description="Fetch list of all registered users across departments")
def list_users(
    current_user: User = Depends(role_required('Admin')),
    db: Session = Depends(get_db)
):
    users = db.query(User).order_by(User.created_at.desc()).all()
    return [u.to_dict() for u in users]


@router.put("/users/{id}/role", summary="Update user role", description="Modify role permission assignment for a user")
def update_user_role(
    id: str,
    data: UserRoleUpdateSchema,
    request: Request,
    current_user: User = Depends(role_required('Admin')),
    db: Session = Depends(get_db)
):
    new_role = data.role
    if not new_role or new_role not in ['Admin', 'Compliance Officer', 'Legal Reviewer', 'Auditor', 'Viewer']:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or missing role")

    target_user = db.query(User).filter(User.id == id).first()
    if not target_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    old_role = target_user.role
    target_user.role = new_role
    db.commit()

    client_ip = request.client.host if request.client else "System"
    log_audit(current_user.id, "USER_ROLE_UPDATE", f"Updated user {target_user.email} role from {old_role} to {new_role}", ip_address=client_ip)
    return {"msg": "User role updated successfully", "user": target_user.to_dict()}


@router.get("/departments", summary="List all departments", description="Fetch list of all corporate departments")
def list_departments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    depts = db.query(Department).order_by(Department.name.asc()).all()
    return [d.to_dict() for d in depts]


@router.post("/departments", status_code=status.HTTP_201_CREATED, summary="Create new department", description="Add a new organization department")
def create_department(
    data: DepartmentCreateSchema,
    request: Request,
    current_user: User = Depends(role_required('Admin')),
    db: Session = Depends(get_db)
):
    name = data.name
    description = data.description or ""

    if not name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Department name is required")

    if db.query(Department).filter(Department.name == name).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Department with this name already exists")

    dept = Department(name=name, description=description)
    db.add(dept)
    db.commit()
    db.refresh(dept)

    client_ip = request.client.host if request.client else "System"
    log_audit(current_user.id, "DEPARTMENT_CREATE", f"Created department: {name}", ip_address=client_ip)
    return {"msg": "Department created successfully", "department": dept.to_dict()}


@router.get("/audit-logs", summary="List system audit logs", description="Fetch recent security and system audit log events")
def list_audit_logs(
    current_user: User = Depends(role_required('Admin', 'Compliance Officer')),
    db: Session = Depends(get_db)
):
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(100).all()
    return [log.to_dict() for log in logs]
