from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from app.core.database import get_db
from app.models import tenant
from app.models.user import User
from app.models.tenant import Tenant
from app.core.config import settings  # فرض: secret و algorithm اینجا تعریف شده

# -------------------------
# User dependency
# -------------------------


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(
        settings.oauth2_scheme
    ),  # فرض: OAuth2PasswordBearer در settings تعریف شده
) -> User:
    """
    کاربر جاری را از روی JWT توکن resolve می‌کند.
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
            )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    user = db.query(User).filter(User.id == int(user_id), User.tenant_id == tenant.id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
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
    Tenant را از user جاری resolve می‌کند و در request context inject می‌کند.
    - tenant_id از relation کاربر گرفته می‌شود.
    - اگر tenant وجود نداشت یا mismatch بود → 403.
    """
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant not found or mismatch",
        )
    return tenant
