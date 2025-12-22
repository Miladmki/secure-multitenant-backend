from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import Optional

from app.models.user import User
from app.models.tenant import Tenant
from app.models.refresh_token import RefreshToken
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)


# Keep services pure business logic
class AuthError(Exception):
    pass


REFRESH_TOKEN_TTL_MINUTES = 60 * 24 * 7  # 7 days


def _refresh_expiry() -> datetime:
    return datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_TTL_MINUTES)


def register_user(db: Session, tenant: Tenant, user_in) -> User:
    existing = (
        db.query(User)
        .filter(User.email == user_in.email, User.tenant_id == tenant.id)
        .first()
    )
    if existing:
        raise AuthError("Email already registered")
    user = User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        tenant_id=tenant.id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, tenant: Tenant, email: str, password: str) -> dict:
    user = (
        db.query(User).filter(User.email == email, User.tenant_id == tenant.id).first()
    )
    if not user or not verify_password(password, user.hashed_password):
        raise AuthError("Invalid credentials")

    access = create_access_token(subject=str(user.id))
    refresh = create_refresh_token(subject=str(user.id))

    rt = RefreshToken(
        user_id=user.id,
        tenant_id=tenant.id,
        token=refresh,
        expires_at=_refresh_expiry(),
    )
    db.add(rt)
    db.commit()

    return {"access_token": access, "refresh_token": refresh, "token_type": "bearer"}


def refresh_tokens(db: Session, tenant: Tenant, refresh_token: str) -> dict:
    rt = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.token == refresh_token, RefreshToken.tenant_id == tenant.id
        )
        .first()
    )
    if not rt or rt.expires_at <= datetime.utcnow():
        # Match test expectation text
        raise AuthError("Invalid or expired refresh token")

    user = (
        db.query(User)
        .filter(User.id == rt.user_id, User.tenant_id == tenant.id)
        .first()
    )
    if not user:
        raise AuthError("Invalid or expired refresh token")

    new_access = create_access_token(subject=str(user.id))
    new_refresh = create_refresh_token(subject=str(user.id))

    rt.token = new_refresh
    rt.expires_at = _refresh_expiry()
    db.commit()

    return {
        "access_token": new_access,
        "refresh_token": new_refresh,
        "token_type": "bearer",
    }


def logout_user(db: Session, tenant: Tenant, refresh_token: str) -> None:
    rt = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.token == refresh_token, RefreshToken.tenant_id == tenant.id
        )
        .first()
    )
    if not rt:
        return
    db.delete(rt)
    db.commit()
