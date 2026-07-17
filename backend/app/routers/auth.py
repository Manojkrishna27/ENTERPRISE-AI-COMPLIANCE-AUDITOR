import uuid
from flask import Blueprint, request, jsonify
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity
from app.database import db
from app.models.user import User, Department
from app.utils.security import log_audit

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')
    full_name = data.get('full_name')
    department_id = data.get('department_id')
    role = data.get('role', 'Viewer')  # Default role

    if not email or not password or not full_name:
        return jsonify({"msg": "Missing required fields (email, password, full_name)"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"msg": "User with this email already exists"}), 409

    # Verify department if provided
    if department_id:
        dept = Department.query.get(department_id)
        if not dept:
            return jsonify({"msg": "Invalid department_id"}), 400

    user = User(
        email=email,
        full_name=full_name,
        role=role,
        department_id=department_id,
        is_verified=False,
        verification_token=str(uuid.uuid4())
    )
    user.set_password(password)
    
    db.session.add(user)
    db.session.commit()

    log_audit(user.id, "USER_REGISTER", f"Registered new account: {email}")

    return jsonify({
        "msg": "User registered successfully. Please verify your email.",
        "user": user.to_dict()
    }), 201


@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({"msg": "Email and password are required"}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({"msg": "Invalid email or password"}), 401

    if not user.is_active:
        return jsonify({"msg": "Account is deactivated"}), 403

    # Generate JWT with custom claims
    additional_claims = {
        "role": user.role,
        "name": user.full_name,
        "email": user.email
    }
    access_token = create_access_token(identity=user.id, additional_claims=additional_claims)

    log_audit(user.id, "USER_LOGIN", f"Logged in successfully")

    return jsonify({
        "access_token": access_token,
        "user": user.to_dict()
    }), 200


@auth_bp.route('/me', methods=['GET'])
@jwt_required()
def me():
    user_id = get_jwt_identity()
    user = User.query.get(user_id)
    if not user:
        return jsonify({"msg": "User not found"}), 404
    return jsonify(user.to_dict()), 200


@auth_bp.route('/forgot-password', methods=['POST'])
def forgot_password():
    data = request.get_json() or {}
    email = data.get('email')
    if not email:
        return jsonify({"msg": "Email is required"}), 400

    user = User.query.filter_by(email=email).first()
    if user:
        user.reset_token = str(uuid.uuid4())
        db.session.commit()
        log_audit(user.id, "PASSWORD_FORGOT", "Requested password reset token")
        # In a real environment, send an email. For this implementation, return token in payload for developer visibility.
        return jsonify({
            "msg": "Password reset token generated.",
            "reset_token": user.reset_token
        }), 200
    
    return jsonify({"msg": "If the email exists, a reset token has been sent."}), 200


@auth_bp.route('/reset-password', methods=['POST'])
def reset_password():
    data = request.get_json() or {}
    token = data.get('token')
    new_password = data.get('password')

    if not token or not new_password:
        return jsonify({"msg": "Token and password are required"}), 400

    user = User.query.filter_by(reset_token=token).first()
    if not user:
        return jsonify({"msg": "Invalid or expired reset token"}), 400

    user.set_password(new_password)
    user.reset_token = None
    db.session.commit()

    log_audit(user.id, "PASSWORD_RESET", "Reset password via token")

    return jsonify({"msg": "Password has been reset successfully"}), 200


@auth_bp.route('/verify-email', methods=['POST'])
def verify_email():
    data = request.get_json() or {}
    token = data.get('token')

    if not token:
        return jsonify({"msg": "Verification token is required"}), 400

    user = User.query.filter_by(verification_token=token).first()
    if not user:
        return jsonify({"msg": "Invalid or expired verification token"}), 400

    user.is_verified = True
    user.verification_token = None
    db.session.commit()

    log_audit(user.id, "EMAIL_VERIFY", "Verified email address")

    return jsonify({"msg": "Email verified successfully"}), 200
