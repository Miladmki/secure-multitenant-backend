from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_tenant
from app.models.tenant import Tenant
from app.schemas.user import UserCreate, UserPublic
from app.schemas.token import Token
from app.services import auth_service

router = APIRouter()


@router.post("/auth/register", response_model=UserPublic, status_code=201)
def register(
    user_in: UserCreate,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    return auth_service.register_user(db, tenant, user_in)


@router.post("/auth/login", response_model=Token, status_code=200)
async def login(
    request: Request,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
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

    return auth_service.authenticate_user(db, tenant, email, password)


@router.post("/auth/refresh", response_model=Token, status_code=200)
def refresh_token_endpoint(
    payload: dict,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    token = payload.get("refresh_token")
    if not token:
        raise HTTPException(status_code=422, detail="refresh_token is required")

    return auth_service.refresh_tokens(db, tenant, token)


@router.post("/auth/logout", status_code=204)
def logout(
    payload: dict,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    token = payload.get("refresh_token")
    if not token:
        raise HTTPException(status_code=422, detail="refresh_token is required")

    auth_service.logout_user(db, tenant, token)
    return
