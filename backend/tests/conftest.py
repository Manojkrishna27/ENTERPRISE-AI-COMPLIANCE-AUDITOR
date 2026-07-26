import pytest
from app.core.database import Base, SessionLocal, engine
from app.main import app
from app.models.user import Department, User
from fastapi.testclient import TestClient


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


@pytest.fixture
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
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
            is_active=True,
        )
        user.set_password("password123")
        session.add(user)

    session.commit()
    session.close()
    yield
