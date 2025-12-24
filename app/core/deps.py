# app/core/deps.py

from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.core.database import get_db
from app.core.config import settings
from app.core.security import oauth2_scheme

from app.models.user import User
from app.models.tenant import Tenant

from app.core.authorization import (
    resolve_permission,
    AuthorizationError,
)

# =====================================================
# AUTHENTICATION
# =====================================================


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    """
    Resolve authenticated user from JWT access token.
    """
    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm],
        )
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
        )

    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user


# =====================================================
# TENANT CONTEXT
# =====================================================


def get_current_tenant(
    tenant_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Tenant:
    """
    Resolve tenant and enforce hard tenant isolation.
    """
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )

    # 🔐 Hard tenant isolation (non-negotiable)
    if current_user.tenant_id != tenant.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cross-tenant access denied",
        )

    return tenant


# =====================================================
# AUTHORIZATION (PERMISSION-BASED, CENTRALIZED)
# =====================================================


def require_permission(permission: str):
    """
    Centralized permission enforcement dependency.

    Features:
    - Role → permission mapping
    - Permission scopes (wildcards supported)
    - Policy-based authorization
    - Tenant isolation
    - Deny-by-default
    """

    def checker(
        request: Request,
        current_user: User = Depends(get_current_user),
        tenant: Tenant = Depends(get_current_tenant),
    ) -> None:
        # Optional: resource owner id for self-access policies
        resource_owner_id = None

        if "user_id" in request.path_params:
            try:
                resource_owner_id = int(request.path_params["user_id"])
            except ValueError:
                pass

        try:
            resolve_permission(
                user=current_user,
                tenant=tenant,
                permission=permission,
                resource_owner_id=resource_owner_id,
            )
        except AuthorizationError as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e),
            )

        return None

    return checker


# =====================================================
# LEGACY ROLE-BASED CHECKS (DEPRECATED)
# =====================================================


def require_role(role_name: str):
    """
    ⚠️ DEPRECATED
    Legacy role-based authorization.
    Do NOT use in new code.
    """

    def checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        roles = {role.name for role in current_user.roles}
        if role_name not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden",
            )
        return current_user

    return checker


def require_global_role(role_name: str):
    """
    ⚠️ DEPRECATED
    Global role check (e.g. superadmin).
    """

    def checker(
        current_user: User = Depends(get_current_user),
    ) -> User:
        roles = {role.name for role in current_user.roles}
        if role_name not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden",
            )
        return current_user

    return checker
