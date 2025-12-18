from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.deps import get_current_user, get_db, require_role
from app.models.user import User
from app.models.tenant import Tenant

router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.get("/{tenant_id}/dashboard")
def tenant_dashboard(
    tenant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # بررسی tenant isolation
    if current_user.tenant_id != tenant_id:
        raise HTTPException(status_code=403, detail="Forbidden: tenant mismatch")

    # بررسی نقش admin
    if not any(role.name == "admin" for role in current_user.roles):
        raise HTTPException(status_code=403, detail="Forbidden: role mismatch")

    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    return {"msg": f"Welcome admin to tenant {tenant.name} dashboard"}
