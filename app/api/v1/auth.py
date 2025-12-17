# app/api/v1/auth.py
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
)
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.schemas.user import UserCreate, RefreshRequest

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == user_in.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user = User(
        email=user_in.email,
        hashed_password=hash_password(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"id": user.id, "email": user.email}


@router.post("/login", status_code=status.HTTP_200_OK)
async def login(
    request: Request,
    db: Session = Depends(get_db),
):
    # تشخیص نوع ورودی
    content_type = request.headers.get("Content-Type", "")
    if "application/x-www-form-urlencoded" in content_type:
        form = await request.form()
        email = form.get("username")
        password = form.get("password")
    else:
        try:
            body = await request.json()
        except Exception:
            raise HTTPException(status_code=422, detail="Invalid login payload")
        email = body.get("email")
        password = body.get("password")

    if not email or not password:
        raise HTTPException(status_code=422, detail="Invalid login payload")

    user = db.query(User).filter(User.email == email).first()
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = create_access_token(subject=str(user.id))
    refresh_token_value, expires_at = create_refresh_token()

    db.add(
        RefreshToken(token=refresh_token_value, user_id=user.id, expires_at=expires_at)
    )
    db.commit()

    return {
        "access_token": access_token,
        "refresh_token": refresh_token_value,
        "token_type": "bearer",
    }


@router.post("/refresh", status_code=status.HTTP_200_OK)
def refresh_access_token(
    payload: RefreshRequest,
    db: Session = Depends(get_db),
):
    token = (
        db.query(RefreshToken)
        .filter(RefreshToken.token == payload.refresh_token)
        .first()
    )

    if not token or token.revoked or token.expires_at < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    # rotate refresh token
    token.revoked = True

    new_access_token = create_access_token(subject=str(token.user_id))
    new_refresh_value, new_expires = create_refresh_token()

    db.add(
        RefreshToken(
            token=new_refresh_value, user_id=token.user_id, expires_at=new_expires
        )
    )
    db.commit()

    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_value,
        "token_type": "bearer",
    }
