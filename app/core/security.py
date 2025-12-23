from datetime import datetime, timedelta, timezone
from typing import Optional, Union, Dict, Any
import uuid

from jose import jwt, JWTError
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings


# -------------------------
# Password hashing
# -------------------------
pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
)


def get_password_hash(password: str) -> str:
    """
    Hash plain password using Argon2.
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify password against stored hash.
    """
    return pwd_context.verify(plain_password, hashed_password)


# -------------------------
# OAuth2 scheme
# -------------------------
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# -------------------------
# JWT helpers
# -------------------------
def create_access_token(
    subject: Union[str, Dict[str, Any]],
    expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Create short-lived access token.

    Compatible with:
    - subject as str (user_id)            ← legacy/tests
    - subject as dict payload             ← production usage
    """

    expire = datetime.now(timezone.utc) + (
        expires_delta
        if expires_delta
        else timedelta(minutes=settings.access_token_expire_minutes)
    )

    if isinstance(subject, str):
        payload: Dict[str, Any] = {"sub": subject}
    elif isinstance(subject, dict):
        payload = subject.copy()
    else:
        raise TypeError("subject must be str or dict")

    payload.update(
        {
            "exp": expire,
            "type": "access",
        }
    )

    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm=settings.algorithm,
    )


def create_refresh_token(subject: Union[str, Dict[str, Any]]) -> str:
    """
    Create JWT refresh token (NOT USED by auth_service, but kept for compatibility).
    """

    if isinstance(subject, str):
        payload: Dict[str, Any] = {"sub": subject}
    elif isinstance(subject, dict):
        payload = subject.copy()
    else:
        raise TypeError("subject must be str or dict")

    payload.update(
        {
            "jti": str(uuid.uuid4()),
            "type": "refresh",
        }
    )

    return jwt.encode(
        payload,
        settings.secret_key,
        algorithm=settings.algorithm,
    )


def decode_token(token: str) -> dict:
    """
    Decode and validate JWT token.
    """
    try:
        return jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
    except JWTError:
        raise ValueError("Invalid or expired token")
