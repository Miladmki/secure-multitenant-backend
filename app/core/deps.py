# app/core/deps.py
from enum import Enum
from app.core.permissions import Permission

from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from enum import Enum

from app.core.database import get_db
from app.core.config import settings
from app.core.security import oauth2_scheme

from app.models.user import User
from app.models.tenant import Tenant

from app.core.authorization import resolve_permission, AuthorizationError
from app.services.audit_service import log_authorization_decision


# =====================================================
# AUTHENTICATION
# =====================================================


def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
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
# TENANT RESOLUTION
# =====================================================


def get_current_tenant(
    tenant_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Tenant:
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )

    if current_user.tenant_id != tenant.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cross-tenant access denied",
        )

    return tenant


def get_current_user_tenant(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Tenant:
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User has no tenant",
        )

    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )

    return tenant


# =====================================================
# AUTHORIZATION + AUDIT LOGGING
# =====================================================


def _normalize_permission(permission: str | Enum) -> str:
    """
    Ensures permissions are logged as their canonical string value.
    """
    if isinstance(permission, Enum):
        return permission.value
    return str(permission)


def require_permission(permission: Permission):
    def checker(
        request: Request,
        current_user: User = Depends(get_current_user),
        tenant: Tenant = Depends(get_current_user_tenant),
        db: Session = Depends(get_db),
    ) -> None:
        resource_owner_id = None
        allowed = False
        reason = "unknown"

        if "user_id" in request.path_params:
            try:
                resource_owner_id = int(request.path_params["user_id"])
            except ValueError:
                pass

        try:
            resolve_permission(
                user=current_user,
                tenant=tenant,
                permission=permission,  # ENUM, not str
                resource_owner_id=resource_owner_id,
            )
            allowed = True
            reason = "permission granted"

        except AuthorizationError as e:
            allowed = False
            reason = str(e)

        finally:
            try:
                log_authorization_decision(
                    db=db,
                    user_id=current_user.id if current_user else None,
                    tenant_id=tenant.id if tenant else None,
                    permission=permission.value,  # string only for audit
                    allowed=allowed,
                    reason=reason,
                    endpoint=request.url.path,
                    method=request.method,
                    context={"resource_owner_id": resource_owner_id},
                )
            except Exception:
                pass

        if not allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=reason,
            )

    return checker
