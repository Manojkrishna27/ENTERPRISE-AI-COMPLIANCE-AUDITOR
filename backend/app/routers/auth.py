import uuid
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token
from app.core.dependencies import get_current_user
from app.models.user import User, Department
from app.utils.security import log_audit
from app.services.redis_service import redis_service
from app.schemas.auth import (
    UserRegisterSchema,
    UserLoginSchema,
    ForgotPasswordSchema,
    ResetPasswordSchema,
    VerifyEmailSchema
)

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.get("/departments", summary="List departments for signup", description="Fetch public list of available departments for user registration")
def public_list_departments(db: Session = Depends(get_db)):
    depts = db.query(Department).order_by(Department.name.asc()).all()
    return [d.to_dict() for d in depts]

@router.post("/register", status_code=status.HTTP_201_CREATED, summary="Register a new user", description="Register a new user in the compliance system")
def register(data: UserRegisterSchema, request: Request, db: Session = Depends(get_db)):
    if not data.email or not data.password or not data.full_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing required fields (email, password, full_name)")

    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User with this email already exists")

    if data.department_id:
        dept = db.query(Department).filter(Department.id == data.department_id).first()
        if not dept:
            legal_dept = db.query(Department).filter(Department.name == 'Legal').first()
            data.department_id = legal_dept.id if legal_dept else None

    auto_verify = not settings.EMAIL_VERIFICATION_ENABLED
    user = User(
        email=data.email,
        full_name=data.full_name,
        role=data.role or 'Viewer',
        department_id=data.department_id,
        is_verified=auto_verify,
        verification_token=None if auto_verify else str(uuid.uuid4())
    )
    user.set_password(data.password)
    
    db.add(user)
    db.commit()
    db.refresh(user)

    client_ip = request.client.host if request.client else "System"
    log_audit(user.id, "USER_REGISTER", f"Registered new account: {user.email} (auto_verified={auto_verify})", ip_address=client_ip)

    msg = "User registered successfully! Account is ready for login." if auto_verify else "User registered successfully. Please verify your email."
    return {
        "msg": msg,
        "user": user.to_dict()
    }


@router.post("/login", summary="Login and get JWT tokens", description="Authenticate user credentials and return access JWT token")
def login(data: UserLoginSchema, request: Request, db: Session = Depends(get_db)):
    if not data.email or not data.password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email and password are required")

    user = db.query(User).filter(User.email == data.email).first()
    if not user or not user.check_password(data.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is deactivated")

    additional_claims = {
        "role": user.role,
        "name": user.full_name,
        "email": user.email
    }
    access_token = create_access_token(subject=user.id, additional_claims=additional_claims)

    client_ip = request.client.host if request.client else "System"
    log_audit(user.id, "USER_LOGIN", "Logged in successfully", ip_address=client_ip)

    return {
        "access_token": access_token,
        "user": user.to_dict()
    }


@router.get("/me", summary="Get current user profile", description="Fetch current authenticated user details")
def me(current_user: User = Depends(get_current_user)):
    return current_user.to_dict()


@router.post("/logout", summary="Logout user", description="Revoke current access token and add to Redis blocklist")
def logout(request: Request, current_user: User = Depends(get_current_user)):
    jti = getattr(current_user, "_current_jti", None)
    if jti:
        redis_service.add_token_to_blocklist(jti, 3600)
        
    client_ip = request.client.host if request.client else "System"
    log_audit(current_user.id, "USER_LOGOUT", "Logged out and revoked token", ip_address=client_ip)
    return {"msg": "Successfully logged out"}


@router.post("/forgot-password", summary="Request password reset", description="Generate password reset token for account recovery")
def forgot_password(data: ForgotPasswordSchema, request: Request, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == data.email).first()
    if user:
        user.reset_token = str(uuid.uuid4())
        db.commit()
        client_ip = request.client.host if request.client else "System"
        log_audit(user.id, "PASSWORD_FORGOT", "Requested password reset token", ip_address=client_ip)
        return {
            "msg": "Password reset token generated.",
            "reset_token": user.reset_token
        }
    return {"msg": "If the email exists, a reset token has been sent."}


@router.post("/reset-password", summary="Reset user password", description="Reset user password using reset token")
def reset_password(data: ResetPasswordSchema, request: Request, db: Session = Depends(get_db)):
    if not data.token or not data.password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token and password are required")

    user = db.query(User).filter(User.reset_token == data.token).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired reset token")

    user.set_password(data.password)
    user.reset_token = None
    db.commit()

    client_ip = request.client.host if request.client else "System"
    log_audit(user.id, "PASSWORD_RESET", "Reset password via token", ip_address=client_ip)
    return {"msg": "Password has been reset successfully"}


@router.post("/verify-email", summary="Verify email address", description="Verify user email address using verification token")
def verify_email(data: VerifyEmailSchema, request: Request, db: Session = Depends(get_db)):
    if not data.token:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification token is required")

    user = db.query(User).filter(User.verification_token == data.token).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid or expired verification token")

    user.is_verified = True
    user.verification_token = None
    db.commit()

    client_ip = request.client.host if request.client else "System"
    log_audit(user.id, "EMAIL_VERIFY", "Verified email address", ip_address=client_ip)
    return {"msg": "Email verified successfully"}
