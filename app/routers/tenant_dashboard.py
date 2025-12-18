from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.deps import get_current_user, get_current_tenant
from app.models.user import User
from app.models.tenant import Tenant
from app.services import tenant_service

router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.get("/dashboard", status_code=200)
def tenant_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    tenant: Tenant = Depends(get_current_tenant),
):
    return tenant_service.get_dashboard_data(db, tenant, current_user)
