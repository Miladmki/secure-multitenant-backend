# app/api/v1/auth.py
from fastapi import APIRouter, Depends, HTTPException, Request, Body, status
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.models.tenant import Tenant
from app.schemas.user import UserCreate, UserPublic
from app.schemas.token import Token
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


def _get_default_tenant(db: Session) -> Optional[Tenant]:
    return db.query(Tenant).first()


@router.post(
    "/register", response_model=UserPublic, status_code=status.HTTP_201_CREATED
)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    tenant = _get_default_tenant(db)
    if not tenant:
        raise HTTPException(status_code=500, detail="No tenant available")

    try:
        return auth_service.register_user(db, tenant, user_in)
    except auth_service.AuthError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
async def login(request: Request, db: Session = Depends(get_db)):
    content_type = request.headers.get("content-type", "")
    email = password = None

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

    tenant = _get_default_tenant(db)
    if not tenant:
        raise HTTPException(status_code=500, detail="No tenant available")

    try:
        return auth_service.authenticate_user(db, tenant, email, password)
    except auth_service.AuthError as e:
        raise HTTPException(status_code=401, detail=str(e))


@router.post("/refresh", response_model=Token, status_code=status.HTTP_200_OK)
def refresh_token(payload: dict = Body(...), db: Session = Depends(get_db)):
    token = payload.get("refresh_token")
    if not token:
        raise HTTPException(status_code=422, detail="refresh_token is required")

    tenant = _get_default_tenant(db)
    if not tenant:
        raise HTTPException(status_code=500, detail="No tenant available")

    try:
        return auth_service.refresh_tokens(db, tenant, token)
    except auth_service.AuthError as e:
        # return HTTP 401 with the same error text
        raise HTTPException(status_code=401, detail=str(e))
