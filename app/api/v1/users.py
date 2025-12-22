from fastapi import APIRouter, Depends
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.user import UserPublic

router = APIRouter(prefix="/api/v1/users", tags=["users"])


@router.get("/me", response_model=UserPublic, status_code=200)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user
