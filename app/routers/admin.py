from fastapi import APIRouter, Depends

from app.core.deps import get_current_user, require_permission
from app.core.permissions import Permission
from app.models.user import User

router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)


@router.get("/dashboard")
def admin_dashboard(
    current_user: User = Depends(get_current_user),
    _: None = Depends(require_permission(Permission.ADMIN_DASHBOARD)),
):
    return {"msg": f"Welcome admin {current_user.email}"}
