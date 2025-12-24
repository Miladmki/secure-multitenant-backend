# app/routers/tenant_dashboard.py

from fastapi import APIRouter, Depends

from app.core.deps import get_current_tenant, require_permission
from app.core.permissions import Permissions

from app.models.tenant import Tenant

router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.get(
    "/{tenant_id}/dashboard",
    status_code=200,
    dependencies=[Depends(require_permission(Permissions.TENANT_DASHBOARD_READ))],
)
def tenant_admin_dashboard(
    tenant: Tenant = Depends(get_current_tenant),
):
    return {
        "msg": "Welcome admin",
        "tenant": tenant.name,
    }
