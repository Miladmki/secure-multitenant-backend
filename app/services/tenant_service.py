from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.models.tenant import Tenant


def get_dashboard_data(db: Session, tenant: Tenant, current_user: User) -> dict:
    """
    جمع‌آوری داده‌های داشبورد tenant.
    فقط نقش admin مجاز است.
    """
    # بررسی نقش کاربر
    if not any(role.name == "admin" for role in current_user.roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
        )

    # مثال: جمع‌آوری آمار کاربران
    user_count = db.query(User).filter(User.tenant_id == tenant.id).count()

    return {
        "tenant": tenant.name,
        "user_count": user_count,
        "msg": f"Welcome admin to tenant {tenant.name} dashboard",
    }
