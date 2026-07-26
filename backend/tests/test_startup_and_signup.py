import uuid

from app.core.config import settings
from app.main import init_db_and_seed
from app.models.user import Department, User


def test_init_db_and_seed(db_session):
    """Test that startup initialization idempotently seeds departments and system admin."""
    init_db_and_seed()

    # Verify departments exist (either pre-existing or newly seeded)
    departments = db_session.query(Department).all()
    assert len(departments) >= 1

    # Verify an Admin user exists
    admin = db_session.query(User).filter(User.role == "Admin").first()
    assert admin is not None
    assert admin.is_verified is True
    assert admin.is_active is True

    # Run again to verify idempotency (no duplicate errors or duplicate entries)
    init_db_and_seed()
    depts_after = db_session.query(Department).all()
    assert len(depts_after) == len(departments)


def test_public_departments_endpoint(client):
    """Test that unauthenticated users can fetch departments for signup dropdown."""
    response = client.get("/api/auth/departments")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "id" in data[0]
    assert "name" in data[0]


def test_registration_with_auto_verify(client, db_session):
    """Test user registration when EMAIL_VERIFICATION_ENABLED is False (auto-verify)."""
    settings.EMAIL_VERIFICATION_ENABLED = False

    email = f"user_auto_{uuid.uuid4().hex[:8]}@example.com"
    payload = {
        "email": email,
        "password": "Password123!",
        "full_name": "Auto Verify User",
        "role": "Viewer",
    }

    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    res_json = response.json()
    assert "ready for login" in res_json["msg"]

    # Verify in DB
    user = db_session.query(User).filter(User.email == email).first()
    assert user is not None
    assert user.is_verified is True
    assert user.verification_token is None

    # Verify login works immediately
    login_res = client.post(
        "/api/auth/login", json={"email": email, "password": "Password123!"}
    )
    assert login_res.status_code == 200
    assert "access_token" in login_res.json()


def test_registration_with_email_verification_required(client, db_session):
    """Test user registration when EMAIL_VERIFICATION_ENABLED is True."""
    settings.EMAIL_VERIFICATION_ENABLED = True

    email = f"user_req_{uuid.uuid4().hex[:8]}@example.com"
    payload = {
        "email": email,
        "password": "Password123!",
        "full_name": "Verify Required User",
        "role": "Viewer",
    }

    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 201
    res_json = response.json()
    assert "verify your email" in res_json["msg"]

    # Verify in DB
    user = db_session.query(User).filter(User.email == email).first()
    assert user is not None
    assert user.is_verified is False
    assert user.verification_token is not None

    # Reset setting back to default
    settings.EMAIL_VERIFICATION_ENABLED = False
