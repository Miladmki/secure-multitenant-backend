from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from jose import jwt, JWTError

from app.core.database import get_db
from app.core.config import settings
from app.core.security import oauth2_scheme

from app.models.user import User
from app.models.tenant import Tenant

from app.core.authorization import resolve_permission, AuthorizationError
from app.core.permissions import Permission


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
    """
    Tenant resolved from URL path.
    HARD tenant isolation.
    """
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
    """
    Tenant resolved from authenticated user.
    Used ONLY when tenant context is implicit.
    """
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
# AUTHORIZATION (PERMISSION-BASED)
# =====================================================


def require_permission(permission: Permission):
    """
    Centralized permission enforcement dependency.

    - GLOBAL permissions → tenant=None
    - TENANT permissions → tenant resolved automatically
    """

    def checker(
        request: Request,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db),
    ) -> None:
        # ---------------------------------------------
        # Resolve resource owner (optional)
        # ---------------------------------------------
        resource_owner_id = None
        if "user_id" in request.path_params:
            try:
                resource_owner_id = int(request.path_params["user_id"])
            except ValueError:
                pass

        # ---------------------------------------------
        # Resolve tenant ONLY if required
        # ---------------------------------------------
        tenant: Tenant | None = None

        if permission not in (Permission.ADMIN_DASHBOARD,):
            # Tenant-scoped permission
            if not current_user.tenant_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Tenant context required",
                )

            tenant = (
                db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
            )

            if not tenant:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Tenant not found",
                )

        # ---------------------------------------------
        # Authorization resolution
        # ---------------------------------------------
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
