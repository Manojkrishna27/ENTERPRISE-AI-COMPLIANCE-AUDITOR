import uuid
from datetime import datetime, timedelta
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext
from werkzeug.security import check_password_hash as werkzeug_check_hash
from werkzeug.security import generate_password_hash as werkzeug_gen_hash

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    if hashed_password.startswith("scrypt:") or hashed_password.startswith("pbkdf2:"):
        return werkzeug_check_hash(hashed_password, plain_password)
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception:
        return werkzeug_check_hash(hashed_password, plain_password)


def get_password_hash(password: str) -> str:
    try:
        return pwd_context.hash(password)
    except Exception:
        return werkzeug_gen_hash(password)


def create_access_token(
    subject: str,
    additional_claims: dict[str, Any] | None = None,
    expires_delta: timedelta | None = None,
) -> str:
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {
        "sub": str(subject),
        "jti": str(uuid.uuid4()),
        "exp": expire,
        "iat": datetime.utcnow(),
    }
    if additional_claims:
        to_encode.update(additional_claims)

    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def decode_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError as e:
        raise e
