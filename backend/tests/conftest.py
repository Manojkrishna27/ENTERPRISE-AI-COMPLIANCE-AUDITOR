import pytest
from app import create_app
from app.database import db
from app.models.user import Department, User

class TestConfig:
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'test-secret'
    REDIS_URL = 'redis://redis:6379/1'  # Separate DB for tests
    USE_LOCAL_STORAGE = True
    LOCAL_STORAGE_DIR = '/tmp/test_uploads'

@pytest.fixture
def app():
    app = create_app(TestConfig)
    
    with app.app_context():
        db.create_all()
        # Seed test data
        dept = Department(name="Test Dept")
        db.session.add(dept)
        db.session.commit()
        
        user = User(
            email="test@example.com",
            password_hash="test",  # simplified
            name="Test User",
            role="Admin",
            department_id=dept.id
        )
        db.session.add(user)
        db.session.commit()
        
        yield app
        
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def test_user(app):
    with app.app_context():
        return User.query.filter_by(email="test@example.com").first()
