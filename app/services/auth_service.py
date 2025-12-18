from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.models.tenant import Tenant
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)
from app.schemas.user import UserCreate
from app.schemas.token import Token


def register_user(db: Session, tenant: Tenant, user_in: UserCreate) -> User:
    existing = (
        db.query(User)
        .filter(User.email == user_in.email, User.tenant_id == tenant.id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        tenant_id=tenant.id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, tenant: Tenant, email: str, password: str) -> Token:
    user = (
        db.query(User).filter(User.email == email, User.tenant_id == tenant.id).first()
    )
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(
        subject=str(user.id), expires_delta=timedelta(minutes=30)
    )
    refresh_token = create_refresh_token(subject=str(user.id))
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)

    db.add(
        RefreshToken(
            token=refresh_token,
            user_id=user.id,
            tenant_id=tenant.id,
            expires_at=expires_at,
        )
    )
    db.commit()

    return Token(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )


def refresh_tokens(db: Session, tenant: Tenant, refresh_token: str) -> Token:
    stored = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.token == refresh_token, RefreshToken.tenant_id == tenant.id
        )
        .first()
    )
    if not stored:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    user = (
        db.query(User)
        .filter(User.id == stored.user_id, User.tenant_id == tenant.id)
        .first()
    )
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired refresh token")

    db.delete(stored)
    db.commit()

    access_token = create_access_token(
        subject=str(user.id), expires_delta=timedelta(minutes=30)
    )
    new_refresh_token = create_refresh_token(subject=str(user.id))
    expires_at = datetime.now(timezone.utc) + timedelta(days=7)

    db.add(
        RefreshToken(
            token=new_refresh_token,
            user_id=user.id,
            tenant_id=tenant.id,
            expires_at=expires_at,
        )
    )
    db.commit()

    return Token(
        access_token=access_token, refresh_token=new_refresh_token, token_type="bearer"
    )


def logout_user(db: Session, tenant: Tenant, refresh_token: str) -> None:
    stored = (
        db.query(RefreshToken)
        .filter(
            RefreshToken.token == refresh_token, RefreshToken.tenant_id == tenant.id
        )
        .first()
    )
    if stored:
        db.delete(stored)
        db.commit()
