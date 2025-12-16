from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
import uuid

from app.core.config import settings


# -------------------------------------------------------------------
# Password hashing
# -------------------------------------------------------------------

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


# -------------------------------------------------------------------
# Access token (JWT)
# -------------------------------------------------------------------


def create_access_token(subject: str) -> str:
    """
    Create a short-lived JWT access token.

    subject: usually user_id (string)
    """
    now = datetime.utcnow()

    payload = {
        "sub": subject,
        "iat": now,
        "exp": now + timedelta(minutes=settings.access_token_expire_minutes),
    }

    encoded_jwt = jwt.encode(
        payload,
        settings.secret_key,
        algorithm=settings.algorithm,
    )

    return encoded_jwt


# -------------------------------------------------------------------
# Refresh token (opaque token)
# -------------------------------------------------------------------


def create_refresh_token() -> tuple[str, datetime]:
    """
    Create a refresh token and its expiration datetime.

    Returns:
        (token, expires_at)
    """
    expires_at = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)

    token = str(uuid.uuid4())

    return token, expires_at
