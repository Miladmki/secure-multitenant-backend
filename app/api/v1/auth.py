# app/api/v1/auth.py
from datetime import timedelta, datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_tenant
from app.models import tenant
from app.models.user import User
from app.models.tenant import Tenant
from app.models.refresh_token import RefreshToken
from app.schemas.user import UserCreate, UserPublic
from app.schemas.token import Token
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)

router = APIRouter()


@router.post("/auth/register", response_model=UserPublic, status_code=201)
def register(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    # بررسی وجود کاربر در tenant جاری
    existing = (
        db.query(User)
        .filter(User.email == user_in.email, User.tenant_id == tenant.id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    # ایجاد کاربر جدید در tenant جاری
    user = User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
        tenant_id=tenant.id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/auth/login", response_model=Token)
async def login(request: Request, db: Session = Depends(get_db)):
    content_type = request.headers.get("content-type", "")
    email = None
    password = None

    if "application/x-www-form-urlencoded" in content_type:
        form = await request.form()
        email = form.get("username")
        password = form.get("password")
    elif "application/json" in content_type:
        body = await request.json()
        email = body.get("email")
        password = body.get("password")

    if not email or not password:
        raise HTTPException(
            status_code=422, detail="email/username and password are required"
        )

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

    db.add(RefreshToken(token=refresh_token, user_id=user.id, expires_at=expires_at))
    db.commit()

    return Token(
        access_token=access_token, refresh_token=refresh_token, token_type="bearer"
    )


@router.post("/auth/refresh", response_model=Token)
def refresh_token_endpoint(payload: dict, db: Session = Depends(get_db)):
    token = payload.get("refresh_token")
    if not token:
        raise HTTPException(status_code=422, detail="refresh_token is required")

    stored = (
        db.query(RefreshToken)
        .filter(RefreshToken.token == token, RefreshToken.tenant_id == tenant.id)
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
        RefreshToken(token=new_refresh_token, user_id=user.id, expires_at=expires_at)
    )
    db.commit()

    return Token(
        access_token=access_token, refresh_token=new_refresh_token, token_type="bearer"
    )


@router.post("/auth/logout", status_code=204)
def logout(payload: dict, db: Session = Depends(get_db)):
    token = payload.get("refresh_token")
    if not token:
        raise HTTPException(status_code=422, detail="refresh_token is required")

    stored = (
        db.query(RefreshToken)
        .filter(RefreshToken.token == token, RefreshToken.tenant_id == tenant.id)
        .first()
    )
    if stored:
        db.delete(stored)
        db.commit()

    return
