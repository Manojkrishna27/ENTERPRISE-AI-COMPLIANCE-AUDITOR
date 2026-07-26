import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

class Settings:
    PROJECT_NAME: str = "Enterprise AI Compliance & Contract Auditor"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"

    SECRET_KEY: str = os.environ.get('SECRET_KEY', 'super-secret-key-change-in-production')
    JWT_SECRET_KEY: str = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30

    EMAIL_VERIFICATION_ENABLED: bool = os.environ.get('EMAIL_VERIFICATION_ENABLED', 'false').lower() == 'true'
    DEFAULT_ADMIN_EMAIL: str = os.environ.get('DEFAULT_ADMIN_EMAIL', 'admin@contractauditor.com')
    DEFAULT_ADMIN_PASSWORD: str = os.environ.get('DEFAULT_ADMIN_PASSWORD', 'AdminSecure123!')

    is_docker: bool = os.path.exists('/.dockerenv') or os.environ.get('RUNNING_IN_DOCKER') == 'true'

    # Database
    db_uri: str = os.environ.get('DATABASE_URL', '')
    if not db_uri:
        if is_docker:
            db_uri = 'postgresql://postgres:postgres@db:5432/contract_compliance'
        else:
            root_db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'compliance.db'))
            db_uri = f'sqlite:///{root_db_path}'
    elif 'db:5432' in db_uri and not is_docker:
        root_db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'compliance.db'))
        db_uri = f'sqlite:///{root_db_path}'

    DATABASE_URL: str = db_uri
    SQLALCHEMY_DATABASE_URI: str = db_uri

    # Vector DB & Redis
    QDRANT_HOST: str = os.environ.get('QDRANT_HOST', 'qdrant' if is_docker else 'localhost')
    QDRANT_PORT: int = int(os.environ.get('QDRANT_PORT', 6333))
    REDIS_URL: str = os.environ.get('REDIS_URL', 'redis://redis:6379/0' if is_docker else 'redis://localhost:6379/0')

    # OpenAI API Key
    OPENAI_API_KEY: str = os.environ.get('OPENAI_API_KEY', '')

    # Storage
    USE_LOCAL_STORAGE: bool = os.environ.get('USE_LOCAL_STORAGE', 'true').lower() == 'true'
    if is_docker:
        LOCAL_STORAGE_DIR: str = os.environ.get('LOCAL_STORAGE_DIR', '/app/uploads')
    else:
        LOCAL_STORAGE_DIR: str = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'uploads')

    AWS_ACCESS_KEY_ID: str = os.environ.get('AWS_ACCESS_KEY_ID', '')
    AWS_SECRET_ACCESS_KEY: str = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
    AWS_S3_BUCKET_NAME: str = os.environ.get('AWS_S3_BUCKET_NAME', '')
    AWS_S3_REGION: str = os.environ.get('AWS_S3_REGION', 'us-east-1')

    # Mail
    MAIL_SERVER: str = os.environ.get('MAIL_SERVER', 'smtp.gmail.com')
    MAIL_PORT: int = int(os.environ.get('MAIL_PORT', 587))
    MAIL_USE_TLS: bool = os.environ.get('MAIL_USE_TLS', 'true').lower() == 'true'
    MAIL_USERNAME: str = os.environ.get('MAIL_USERNAME', '')
    MAIL_PASSWORD: str = os.environ.get('MAIL_PASSWORD', '')
    MAIL_DEFAULT_SENDER: str = os.environ.get('MAIL_DEFAULT_SENDER', 'noreply@contractcompliance.com')

    MAX_CONTENT_LENGTH: int = 50 * 1024 * 1024  # 50MB

settings = Settings()
Config = settings
