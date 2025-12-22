from fastapi import APIRouter, Depends
from app.core.deps import get_current_tenant, require_role
from app.models.tenant import Tenant
from app.models.user import User

router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.get("/{tenant_id}/dashboard", status_code=200)
def tenant_admin_dashboard(
    tenant: Tenant = Depends(get_current_tenant),
    current_user: User = Depends(require_role("admin")),
):
    return {"msg": "Welcome admin", "tenant": tenant.name}
