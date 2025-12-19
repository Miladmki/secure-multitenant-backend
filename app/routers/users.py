from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_tenant
from app.models.tenant import Tenant
from app.services import user_service

router = APIRouter(prefix="/users", tags=["users"])


# -------------------------
# لیست کاربران tenant جاری
# -------------------------
@router.get("/", status_code=200)
def list_users_endpoint(
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    return user_service.list_users(db, tenant.id)


# -------------------------
# آپدیت کاربر در tenant جاری
# -------------------------
@router.put("/{user_id}", status_code=200)
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


# -------------------------
# حذف کاربر در tenant جاری
# -------------------------
@router.delete("/{user_id}", status_code=200)
def delete_user_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    ok = user_service.delete_user(db, user_id, tenant.id)
    if not ok:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
        )
    return {"msg": "User deleted"}
