import os
from datetime import timedelta

from dotenv import load_dotenv

# Load environment variables from .env file if it exists
load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "super-secret-key-change-in-production")
    JWT_SECRET_KEY = os.environ.get(
        "JWT_SECRET_KEY", "jwt-secret-key-change-in-production"
    )
    JWT_TOKEN_LOCATION = ("headers", "query_string")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)

    # Enable token blocklisting
    JWT_BLACKLIST_ENABLED = True
    JWT_BLACKLIST_TOKEN_CHECKS = ("access", "refresh")

    # Check if running inside docker container
    is_docker = (
        os.path.exists("/.dockerenv") or os.environ.get("RUNNING_IN_DOCKER") == "true"
    )

    # SQLAlchemy Configuration
    db_uri = os.environ.get("DATABASE_URL")
    if not db_uri:
        if is_docker:
            db_uri = "postgresql://postgres:postgres@db:5432/contract_compliance"
        else:
            db_uri = "sqlite:///compliance.db"
    elif "db:5432" in db_uri and not is_docker:
        db_uri = "sqlite:///compliance.db"

    SQLALCHEMY_DATABASE_URI = db_uri
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Qdrant Vector DB Configuration
    QDRANT_HOST = os.environ.get("QDRANT_HOST", "qdrant" if is_docker else "localhost")
    QDRANT_PORT = int(os.environ.get("QDRANT_PORT", 6333))

    # Redis Configuration
    REDIS_URL = os.environ.get(
        "REDIS_URL", "redis://redis:6379/0" if is_docker else "redis://localhost:6379/0"
    )

    # OpenAI API Key
    OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")

    # Storage Settings
    USE_LOCAL_STORAGE = os.environ.get("USE_LOCAL_STORAGE", "true").lower() == "true"

    if is_docker:
        LOCAL_STORAGE_DIR = os.environ.get("LOCAL_STORAGE_DIR", "/app/uploads")
    else:
        # Resolve to a local uploads directory in the backend directory
        LOCAL_STORAGE_DIR = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads"
        )
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY")
    AWS_S3_BUCKET_NAME = os.environ.get("AWS_S3_BUCKET_NAME")
    AWS_S3_REGION = os.environ.get("AWS_S3_REGION", "us-east-1")

    # Mail Settings
    MAIL_SERVER = os.environ.get("MAIL_SERVER", "smtp.gmail.com")
    MAIL_PORT = int(os.environ.get("MAIL_PORT", 587))
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "true").lower() == "true"
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME", "")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD", "")
    MAIL_DEFAULT_SENDER = os.environ.get(
        "MAIL_DEFAULT_SENDER", "noreply@contractcompliance.com"
    )

    # App Settings
    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max upload size
