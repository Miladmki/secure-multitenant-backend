# app/routers/admin.py

from fastapi import APIRouter, Depends

from app.core.deps import require_permission
from app.core.permissions import Permissions

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get(
    "/dashboard",
    status_code=200,
    dependencies=[Depends(require_permission(Permissions.ADMIN_DASHBOARD_READ))],
)
def admin_global_dashboard():
    return {"msg": "Welcome admin"}
