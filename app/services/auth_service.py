from datetime import datetime, timedelta, timezone
import secrets

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.schemas.user import UserCreate
from app.schemas.token import Token
from app.core.security import (
    verify_password,
    get_password_hash,
    create_access_token,
)
from app.core.config import settings


# ======================
# Errors
# ======================


class AuthError(Exception):
    pass


# ======================
# Helpers
# ======================


def _generate_refresh_token() -> str:
    """
    Generate cryptographically secure opaque refresh token.
    Stored verbatim in DB (NOT JWT).
    """
    return secrets.token_urlsafe(48)


def _refresh_expiry() -> datetime:
    # always return a timezone-aware UTC expiry
    return datetime.now(timezone.utc) + timedelta(
        days=settings.refresh_token_expire_days
    )


# ======================
# Public API
# ======================


def register_user(db: Session, tenant, user_in: UserCreate) -> User:
    existing = (
        db.query(User)
        .filter(
            User.email == user_in.email,
            User.tenant_id == tenant.id,
        )
        .first()
    )
    if existing:
        raise AuthError("Email already registered")

    user = User(
        email=user_in.email,
        hashed_password=get_password_hash(user_in.password),
        tenant_id=tenant.id,
        is_active=True,
    )

    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(
    db: Session,
    tenant,
    email: str,
    password: str,
) -> Token:
    user = (
        db.query(User)
        .filter(
            User.email == email,
            User.tenant_id == tenant.id,
        )
        .first()
    )

    if not user or not verify_password(password, user.hashed_password):
        raise AuthError("Invalid credentials")

    access_token = create_access_token({"sub": str(user.id), "tenant_id": tenant.id})

    refresh_token_value = _generate_refresh_token()

    refresh_token = RefreshToken(
        token=refresh_token_value,
        user_id=user.id,
        tenant_id=tenant.id,
        expires_at=_refresh_expiry(),
    )

    db.add(refresh_token)
    db.commit()

    return Token(
        access_token=access_token,
        refresh_token=refresh_token_value,
        token_type="bearer",
    )


def refresh_tokens(
    db: Session,
    tenant,
    refresh_token_str: str,
):
    """
    Secure Refresh Token Rotation
    - Opaque refresh tokens
    - Single-use
    - No state leakage (generic errors)
    """

    token = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.token == refresh_token_str,
            RefreshToken.tenant_id == tenant.id,
        )
        .first()
    )

    # 🔒 GENERIC FAILURE (no info leak)
    if not token:
        raise AuthError("Invalid or expired refresh token")

    if token.is_revoked:
        raise AuthError("Invalid or expired refresh token")

    if token.is_expired:
        raise AuthError("Invalid or expired refresh token")

    # ----------------------
    # ROTATION
    # ----------------------

    now = datetime.now(timezone.utc)

    token.revoked = True
    token.revoked_at = now

    new_refresh_token_value = _generate_refresh_token()
    token.replaced_by_token = new_refresh_token_value

    new_refresh_token = RefreshToken(
        token=new_refresh_token_value,
        user_id=token.user_id,
        tenant_id=tenant.id,
        expires_at=_refresh_expiry(),
    )

    db.add(new_refresh_token)
    db.commit()

    access_token = create_access_token(
        {"sub": str(token.user_id), "tenant_id": tenant.id}
    )

    return {
        "access_token": access_token,
        "refresh_token": new_refresh_token_value,
        "token_type": "bearer",
    }
