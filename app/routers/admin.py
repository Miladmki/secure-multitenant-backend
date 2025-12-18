from fastapi import APIRouter, Depends, HTTPException, status
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/dashboard")
def admin_dashboard(current_user: User = Depends(get_current_user)):
    if not any(role.name == "admin" for role in current_user.roles):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden: role mismatch"
        )
    return {"msg": "Welcome admin"}
