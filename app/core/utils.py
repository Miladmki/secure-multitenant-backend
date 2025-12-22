# ===== app/core/utils.py =====
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from app.models.tenant import Tenant


def get_scoped_resource_or_forbid(
    db: Session,
    tenant: Tenant,
    model,
    obj_id: int,
):
    obj = (
        db.query(model)
        .filter(
            model.id == obj_id,
            model.tenant_id == tenant.id,
        )
        .first()
    )

    if not obj:
        # 🔐 برای tenant isolation تست‌ها
        # باید 403 بدهد، نه 404
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden",
        )

    return obj
