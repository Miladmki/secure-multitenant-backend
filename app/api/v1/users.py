from fastapi import APIRouter, Depends, HTTPException
from app.core.deps import get_current_user
from app.models.user import User

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
def read_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/")
def list_users(current_user: User = Depends(get_current_user)):
    return []


@router.put("/{user_id}")
def update_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
):
    raise HTTPException(status_code=403, detail="Forbidden")


@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    current_user: User = Depends(get_current_user),
):
    raise HTTPException(status_code=403, detail="Forbidden")
