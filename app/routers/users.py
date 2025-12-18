from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_tenant
from app.models.user import User
from app.models.tenant import Tenant

router = APIRouter(prefix="/users", tags=["users"])


# -------------------------
# لیست کاربران tenant جاری
# -------------------------
@router.get("/")
def list_users(
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    users = db.query(User).filter(User.tenant_id == tenant.id).all()
    return users


# -------------------------
# آپدیت کاربر در tenant جاری
# -------------------------
@router.put("/{user_id}")
def update_user(
    user_id: int,
    email: str,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    user = (
        db.query(User).filter(User.id == user_id, User.tenant_id == tenant.id).first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not found in current tenant",
        )

    user.email = email
    db.commit()
    db.refresh(user)
    return user


# -------------------------
# حذف کاربر در tenant جاری
# -------------------------
@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
):
    user = (
        db.query(User).filter(User.id == user_id, User.tenant_id == tenant.id).first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User not found in current tenant",
        )

    db.delete(user)
    db.commit()
    return {"msg": "User deleted"}
