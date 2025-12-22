from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.core.database import get_db
from app.core.config import settings
from app.models.user import User
from app.models.tenant import Tenant
from app.models.role import Role
from app.core.security import oauth2_scheme


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    try:
        payload = jwt.decode(
            token, settings.secret_key, algorithms=[settings.algorithm]
        )
        user_id: str | None = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401)
    except JWTError:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


def get_current_tenant(
    tenant_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Tenant:
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    # 🔴 CRITICAL FIX: tenant isolation
    if current_user.tenant_id != tenant.id:
        raise HTTPException(status_code=403, detail="Forbidden")

    return tenant


def require_role(role_name: str):
    def checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> User:
        roles = {role.name for role in current_user.roles}
        if role_name not in roles:
            raise HTTPException(status_code=403, detail="Forbidden")
        return current_user

    return checker


def require_global_role(role_name: str):
    def checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        roles = {role.name for role in current_user.roles}
        if role_name not in roles:
            raise HTTPException(status_code=403, detail="Forbidden")
        return current_user

    return checker
