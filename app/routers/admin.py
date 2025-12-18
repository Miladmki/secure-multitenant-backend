from fastapi import APIRouter, Depends
from app.core.deps import require_role
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/dashboard")
def admin_dashboard(current_user: User = Depends(require_role("admin"))):
    return {"msg": f"Welcome admin {current_user.email}"}
