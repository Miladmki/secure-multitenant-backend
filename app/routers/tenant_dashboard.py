# app/routers/tenant_dashboard.py

from fastapi import APIRouter, Depends

from app.core.deps import get_current_tenant, require_permission
from app.core.permissions import Permission

router = APIRouter(
    prefix="/tenants",
    tags=["tenants"],
)


@router.get(
    "/{tenant_id}/dashboard",
    dependencies=[
        Depends(get_current_tenant),
        Depends(require_permission(Permission.TENANT_ADMIN)),
    ],
)
def tenant_dashboard():
    return {"msg": "Tenant admin dashboard"}
