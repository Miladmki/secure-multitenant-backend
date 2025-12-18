from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user, get_current_tenant
from app.models.user import User
from app.models.tenant import Tenant

router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.get("/dashboard")
def tenant_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant: Tenant = Depends(get_current_tenant),
):
    # فقط نقش admin مجاز است
    if not any(role.name == "admin" for role in current_user.roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: role mismatch",
        )

    return {"msg": f"Welcome admin to tenant {tenant.name} dashboard"}
