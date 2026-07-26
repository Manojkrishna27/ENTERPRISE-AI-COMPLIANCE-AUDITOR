import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import db, SessionLocal
from app.models.user import Department, User

@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c

@pytest.fixture(autouse=True)
def setup_db():
    db.create_all()
    session = SessionLocal()
    
    # Check if test dept exists
    dept = session.query(Department).filter(Department.name == "Test Dept").first()
    if not dept:
        dept = Department(name="Test Dept", description="Test Department")
        session.add(dept)
        session.flush()
        
    user = session.query(User).filter(User.email == "test@example.com").first()
    if not user:
        user = User(
            email="test@example.com",
            full_name="Test User",
            role="Admin",
            department_id=dept.id,
            is_verified=True,
            is_active=True
        )
        user.set_password("password123")
        session.add(user)
        
    session.commit()
    session.close()
    yield
