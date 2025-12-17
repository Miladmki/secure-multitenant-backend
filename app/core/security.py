# app/core/security.py
from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
from app.core.config import settings
import uuid

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(subject: str) -> str:
    now = datetime.utcnow()
    payload = {
        "sub": subject,
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
    }

    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm=settings.algorithm,
    )


def create_refresh_token() -> tuple[str, datetime]:
    token = str(uuid.uuid4())
    expires_at = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
    return token, expires_at
