from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status

from app.models.user import User
from app.models.tenant import Tenant
from app.security.password import hash_password, verify_password
from app.core.deps import get_current_tenant


def create_user(
    db: Session,
    email: str,
    password: str,
    tenant: Tenant = Depends(get_current_tenant),
) -> User:
    """
    ایجاد کاربر جدید در tenant جاری.
    - tenant_id از context تزریق می‌شود.
    - ورودی آزاد برای tenant_id مجاز نیست.
    """
    user = User(
        email=email,
        hashed_password=hash_password(password),
        tenant_id=tenant.id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(
    db: Session,
    email: str,
    password: str,
    tenant: Tenant = Depends(get_current_tenant),
) -> User | None:
    """
    احراز هویت کاربر در tenant جاری.
    - علاوه بر ایمیل، tenant_id هم بررسی می‌شود.
    """
    user = (
        db.query(User).filter(User.email == email, User.tenant_id == tenant.id).first()
    )
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user
