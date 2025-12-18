# app/core/deps.py
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.models.tenant import Tenant
from app.core.security import oauth2_scheme, decode_token


# -------------------------
# User dependency
# -------------------------
def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User:
    """
    Resolve current user from JWT token.
    """
    try:
        payload = decode_token(token)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user_id: str = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    return user


# -------------------------
# Tenant dependency
# -------------------------
def get_current_tenant(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Tenant:
    """
    Resolve current tenant from current user.
    """
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant not found or mismatch",
        )
    return tenant


# -------------------------
# Role dependency
# -------------------------
def require_role(role_name: str):
    """
    Dependency برای enforce کردن نقش کاربر.
    استفاده: current_user = Depends(require_role("admin"))
    """
    def role_dependency(current_user: User = Depends(get_current_user)):
        if current_user.role != role_name:
            # پیام خطا ساده و امن، بدون افشای role مورد انتظار
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden",
            )
        return current_user

    return role_dependency
