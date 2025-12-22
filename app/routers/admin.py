from fastapi import APIRouter, Depends
from app.core.deps import require_global_role
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/dashboard", status_code=200)
def admin_global_dashboard(
    current_user: User = Depends(require_global_role("admin")),
):
    return {"msg": "Welcome admin"}
