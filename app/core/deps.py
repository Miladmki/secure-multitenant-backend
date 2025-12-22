# ===== app/core/deps.py =====
from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import oauth2_scheme, decode_token
from app.models.user import User
from app.models.role import Role
from app.models.tenant import Tenant


# -----------------------------
# Authentication
# -----------------------------
def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    try:
        payload = decode_token(token)
    except Exception:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


# -----------------------------
# Tenant resolution
# -----------------------------
def get_current_tenant(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Tenant:
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Tenant context invalid",
        )
    return tenant


# -----------------------------
# Role enforcement (tenant-scoped)
# -----------------------------
def require_role(role_name: str):
    def dependency(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if not any(
            role.name == role_name and role.tenant_id == current_user.tenant_id
            for role in current_user.roles
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden: insufficient role",
            )
        return current_user

    return dependency


# -----------------------------
# Role enforcement (global)
# -----------------------------
def require_global_role(role_name: str):
    def dependency(
        current_user: User = Depends(get_current_user),
    ) -> User:
        if not any(role.name == role_name for role in current_user.roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden: insufficient role",
            )
        return current_user

    return dependency
