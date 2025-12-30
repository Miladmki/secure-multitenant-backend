from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_tenant, require_permission
from app.core.permissions import Permission
from app.models.tenant import Tenant
from app.services import user_service

router = APIRouter(
    prefix="/users",
    tags=["users"],
)


@router.get(
    "/",
    status_code=200,
    dependencies=[Depends(require_permission(Permission.USERS_READ))],
)
def list_users_endpoint(
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    return user_service.list_users(db, tenant.id)


@router.put(
    "/{user_id}",
    status_code=200,
    dependencies=[Depends(require_permission(Permission.USERS_WRITE))],
)
def update_user_endpoint(
    user_id: int,
    email: str,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    updated = user_service.update_user_email(db, user_id, tenant.id, email)
    if not updated:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
        )
    return updated
